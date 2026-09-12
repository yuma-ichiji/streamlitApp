import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta


# =========================
# ページ設定
# =========================

st.set_page_config(
    page_title="為替換算アプリ",
    page_icon="💱",
    layout="centered"
)


# =========================
# タイトル
# =========================

st.title("為替換算アプリ")

st.write(
    "APIから為替レートを取得して、"
    "さまざまな通貨を換算できます。"
)

st.divider()


# =========================
# 通貨一覧
# =========================

currencies = {
    "日本円 (JPY)": "JPY",
    "米ドル (USD)": "USD",
    "ユーロ (EUR)": "EUR",
    "イギリスポンド (GBP)": "GBP",
    "中国人民元 (CNY)": "CNY",
    "韓国ウォン (KRW)": "KRW",
    "豪ドル (AUD)": "AUD",
    "カナダドル (CAD)": "CAD",
    "スイスフラン (CHF)": "CHF",
    "シンガポールドル (SGD)": "SGD",
    "ジンバブエ・ドル (ZWL)": "ZWL"
}


# =========================
# 自動更新設定
# =========================

st.subheader("自動更新")

auto_refresh = st.checkbox(
    "自動更新を有効にする",
    value=False
)

if auto_refresh:

    refresh_seconds = st.selectbox(
        "更新間隔",
        [30, 60, 120, 300],
        format_func=lambda x: f"{x}秒"
    )

    st.info(
        f"{refresh_seconds}秒ごとにページを更新します。"
    )

    # JavaScriptを利用してページを更新
    st.components.v1.html(
        f"""
        <script>
        setTimeout(function() {{
            window.parent.location.reload();
        }}, {refresh_seconds * 1000});
        </script>
        """,
        height=0
    )


# =========================
# 金額入力
# =========================

amount = st.number_input(
    "金額を入力してください",
    min_value=0.0,
    value=10000.0,
    step=100.0
)


# =========================
# 通貨選択
# =========================

col1, col2 = st.columns(2)

with col1:

    from_name = st.selectbox(
        "換算元",
        list(currencies.keys()),
        index=0
    )

with col2:

    to_name = st.selectbox(
        "換算先",
        list(currencies.keys()),
        index=1
    )


from_currency = currencies[from_name]
to_currency = currencies[to_name]


# =========================
# 為替換算
# =========================

if st.button(
    "換算する",
    use_container_width=True
):

    if from_currency == to_currency:

        st.success(
            f"{amount:,.2f} {from_currency} = "
            f"{amount:,.2f} {to_currency}"
        )

    else:

        url = (
            "https://api.frankfurter.app/latest"
            f"?amount={amount}"
            f"&from={from_currency}"
            f"&to={to_currency}"
        )

        try:

            response = requests.get(
                url,
                timeout=10
            )

            response.raise_for_status()

            data = response.json()

            result = data["rates"][to_currency]

            st.success("換算しました！")

            st.metric(
                label=f"{from_currency} → {to_currency}",
                value=f"{result:,.4f} {to_currency}"
            )

            st.write(
                f"{amount:,.2f} {from_currency}"
                f" = "
                f"{result:,.4f} {to_currency}"
            )

            if "date" in data:

                st.caption(
                    f"為替レートの日付：{data['date']}"
                )

        except requests.exceptions.Timeout:

            st.error(
                "APIへの接続がタイムアウトしました。"
            )

        except requests.exceptions.ConnectionError:

            st.error(
                "インターネットに接続できません。"
            )

        except requests.exceptions.HTTPError:

            st.error(
                "為替データを取得できませんでした。"
            )

        except KeyError:

            st.error(
                "この通貨のデータがAPIにありません。"
            )

        except Exception as e:

            st.error(
                f"エラーが発生しました。\n\n{e}"
            )


# =========================
# グラフ
# =========================

st.divider()

st.header("為替レートのグラフ")

st.write(
    f"1 {from_currency} が何 {to_currency} になるかを"
    "過去のデータから表示します。"
)


period = st.selectbox(
    "グラフの期間",
    [
        "過去7日",
        "過去30日",
        "過去90日",
        "過去1年"
    ]
)


today = datetime.now().date()


if period == "過去7日":

    days = 7

elif period == "過去30日":

    days = 30

elif period == "過去90日":

    days = 90

else:

    days = 365


start_date = today - timedelta(days=days)


if st.button(
    "グラフを表示する",
    use_container_width=True
):

    if from_currency == to_currency:

        st.info(
            "同じ通貨なのでレートは1です。"
        )

    else:

        start_date_text = start_date.strftime(
            "%Y-%m-%d"
        )

        end_date_text = today.strftime(
            "%Y-%m-%d"
        )

        history_url = (
            "https://api.frankfurter.app/"
            f"{start_date_text}..{end_date_text}"
            f"?from={from_currency}"
            f"&to={to_currency}"
        )

        try:

            response = requests.get(
                history_url,
                timeout=20
            )

            response.raise_for_status()

            history_data = response.json()

            rates = history_data.get(
                "rates",
                {}
            )

            graph_data = []

            for date, value in rates.items():

                if to_currency in value:

                    graph_data.append({
                        "日付": date,
                        "レート": value[to_currency]
                    })

            df = pd.DataFrame(graph_data)

            if df.empty:

                st.error(
                    "グラフに表示できるデータがありません。"
                )

            else:

                df["日付"] = pd.to_datetime(
                    df["日付"]
                )

                df = df.sort_values(
                    "日付"
                )

                df = df.set_index(
                    "日付"
                )

                st.subheader(
                    f"{from_currency} → {to_currency}"
                )

                st.line_chart(
                    df["レート"],
                    use_container_width=True
                )

                # =========================
                # 統計
                # =========================

                latest = df["レート"].iloc[-1]
                highest = df["レート"].max()
                lowest = df["レート"].min()

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "最新レート",
                        f"{latest:.6f}"
                    )

                with col2:

                    st.metric(
                        "期間内最高",
                        f"{highest:.6f}"
                    )

                with col3:

                    st.metric(
                        "期間内最低",
                        f"{lowest:.6f}"
                    )

        except Exception as e:

            st.error(
                f"グラフを取得できませんでした。\n\n{e}"
            )


# =========================
# 説明
# =========================

st.divider()

st.subheader("このアプリについて")

st.write(
    "このアプリはFrankfurter APIを利用して"
    "為替レートを取得しています。"
)

st.caption(
    "為替レートは変動するため、"
    "実際の銀行や両替所のレートとは異なる場合があります。"
)