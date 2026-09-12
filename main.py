import streamlit as st
import requests

# =========================
# ページ設定
# =========================
st.set_page_config(
    page_title="💱 為替換算アプリ",
    page_icon="💱",
    layout="centered"
)

# =========================
# タイトル
# =========================
st.title("💱 為替換算アプリ")
st.write("APIから最新の為替レートを取得して換算します。")

st.divider()

# =========================
# 通貨一覧
# =========================
currencies = {
    "🇯🇵 日本円 (JPY)": "JPY",
    "🇺🇸 米ドル (USD)": "USD",
    "🇪🇺 ユーロ (EUR)": "EUR",
    "🇬🇧 イギリスポンド (GBP)": "GBP",
    "🇨🇳 中国人民元 (CNY)": "CNY",
    "🇰🇷 韓国ウォン (KRW)": "KRW",
    "🇦🇺 豪ドル (AUD)": "AUD",
    "🇨🇦 カナダドル (CAD)": "CAD",
    "🇨🇭 スイスフラン (CHF)": "CHF",
    "🇸🇬 シンガポールドル (SGD)": "SGD"
}

# =========================
# 入力
# =========================
amount = st.number_input(
    "💰 金額を入力してください",
    min_value=0.0,
    value=10000.0,
    step=100.0
)

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
# 換算ボタン
# =========================
if st.button("💱 換算する", use_container_width=True):

    # 同じ通貨の場合
    if from_currency == to_currency:
        st.success(
            f"{amount:,.2f} {from_currency} = "
            f"{amount:,.2f} {to_currency}"
        )

    else:
        # API URL
        url = (
            "https://api.frankfurter.app/latest"
            f"?amount={amount}"
            f"&from={from_currency}"
            f"&to={to_currency}"
        )

        try:
            # APIにアクセス
            response = requests.get(
                url,
                timeout=10
            )

            # HTTPエラーを確認
            response.raise_for_status()

            # JSONを取得
            data = response.json()

            # 結果を取得
            result = data["rates"][to_currency]

            # =========================
            # 結果表示
            # =========================
            st.success("換算しました！")

            st.metric(
                label=f"{from_currency} → {to_currency}",
                value=f"{result:,.2f} {to_currency}"
            )

            st.write(
                f"**{amount:,.2f} {from_currency}**"
                f" = "
                f"**{result:,.2f} {to_currency}**"
            )

            # =========================
            # レート表示
            # =========================
            rate_url = (
                "https://api.frankfurter.app/latest"
                f"?from={from_currency}"
                f"&to={to_currency}"
            )

            rate_response = requests.get(
                rate_url,
                timeout=10
            )

            rate_response.raise_for_status()

            rate_data = rate_response.json()

            rate = rate_data["rates"][to_currency]

            st.info(
                f"📈 1 {from_currency} = "
                f"{rate:,.4f} {to_currency}"
            )

            # APIの日付
            if "date" in data:
                st.caption(
                    f"為替レートの日付：{data['date']}"
                )

        except requests.exceptions.Timeout:
            st.error(
                "⏱️ APIへの接続がタイムアウトしました。"
            )

        except requests.exceptions.ConnectionError:
            st.error(
                "🌐 インターネットに接続できません。"
            )

        except requests.exceptions.HTTPError:
            st.error(
                "❌ APIでエラーが発生しました。"
            )

        except KeyError:
            st.error(
                "❌ APIから正しい為替データを取得できませんでした。"
            )

        except Exception as e:
            st.error(
                f"❌ 予期しないエラーが発生しました。\n\n{e}"
            )

# =========================
# 説明
# =========================
st.divider()

st.subheader("📖 このアプリについて")

st.write(
    "このアプリはFrankfurter APIから為替レートを取得して、"
    "入力した金額を別の通貨に換算します。"
)

st.caption(
    "※ 為替レートは常に変動するため、実際の銀行・両替所の"
    "レートとは異なる場合があります。"
)