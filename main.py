import streamlit as st
import requests
import pandas as pd
from datetime import datetime,timedelta
import streamlit.components.v1 as components
st.set_page_config(page_title="💱為替レート変換アプリ",page_icon="為替",layout="wide")
st.title("💱為替レート変換アプリ")
st.write("最新の為替レートを使って通貨を変換できます。")
currency_names={
    "AED":"UAEディルハム",
    "AUD":"豪ドル",
    "BGN":"ブルガリア・レフ",
    "BRL":"ブラジル・レアル",
    "CAD":"カナダドル",
    "CHF":"スイスフラン",
    "CNY":"中国人民元",
    "CZK":"チェコ・コルナ",
    "DKK":"デンマーク・クローネ",
    "EUR":"ユーロ",
    "GBP":"イギリスポンド",
    "HKD":"香港ドル",
    "HUF":"ハンガリー・フォリント",
    "IDR":"インドネシア・ルピア",
    "ILS":"イスラエル・シェケル",
    "INR":"インド・ルピー",
    "ISK":"アイスランド・クローナ",
    "JPY":"日本円",
    "KRW":"韓国ウォン",
    "MXN":"メキシコ・ペソ",
    "MYR":"マレーシア・リンギット",
    "NOK":"ノルウェー・クローネ",
    "NZD":"ニュージーランドドル",
    "PHP":"フィリピン・ペソ",
    "PLN":"ポーランド・ズウォティ",
    "RON":"ルーマニア・レウ",
    "SEK":"スウェーデン・クローナ",
    "SGD":"シンガポールドル",
    "THB":"タイ・バーツ",
    "TRY":"トルコ・リラ",
    "USD":"米ドル",
    "ZAR":"南アフリカ・ランド"
}
currencies={}
try:
    currency_response=requests.get("https://api.frankfurter.app/currencies",timeout=10)
    if currency_response.status_code==200:
        api_currencies=currency_response.json()
        for code,name in api_currencies.items():
            japanese_name=currency_names.get(code,name)
            currencies[f"{japanese_name} ({code})"]=code
    else:
        st.error("通貨一覧を取得できませんでした。")
except requests.exceptions.RequestException:
    st.error("通貨一覧を取得できませんでした。")
if not currencies:
    currencies={
        "日本円 (JPY)":"JPY",
        "米ドル (USD)":"USD",
        "ユーロ (EUR)":"EUR"
    }
clock_placeholder=st.empty()
st.subheader("現在時刻")
components.html("""
<div style="text-align:center;font-size:40px;font-weight:bold;">
<div id="clock"></div>
</div>
<script>
function updateClock(){
    const now=new Date();
    const year=now.getFullYear();
    const month=String(now.getMonth()+1).padStart(2,"0");
    const day=String(now.getDate()).padStart(2,"0");
    const hours=String(now.getHours()).padStart(2,"0");
    const minutes=String(now.getMinutes()).padStart(2,"0");
    const seconds=String(now.getSeconds()).padStart(2,"0");
    document.getElementById("clock").textContent=year+"年"+month+"月"+day+"日 "+hours+":"+minutes+":"+seconds;
}
updateClock();
setInterval(updateClock,1000);
</script>
""",height=70)
auto_refresh=st.checkbox("自動更新する",value=False)
refresh_seconds=st.selectbox("更新間隔",[10,30,60,120,300,600],index=0,format_func=lambda x:f"{x}秒")
if st.button("更新",use_container_width=True):
    st.rerun()
if auto_refresh:
    components.html(f"""
    <script>
    setTimeout(function(){{
        window.parent.location.reload();
    }},{refresh_seconds*1000});
    </script>
    """,height=0)
st.divider()
st.subheader("通貨変換")
col1,col2=st.columns(2)
with col1:
    from_name=st.selectbox("変換元の通貨",list(currencies.keys()),index=0)
with col2:
    to_name=st.selectbox("変換先の通貨",list(currencies.keys()),index=1)
amount=st.number_input("金額",min_value=0.0,value=1000.0,step=100.0)
from_currency=currencies[from_name]
to_currency=currencies[to_name]
st.write("")
if st.button("変換する",use_container_width=True):
    if from_currency==to_currency:
        st.success(f"{amount:,.2f} {from_currency} = {amount:,.2f} {to_currency}")
        converted_time=datetime.now()
        st.info(f"変換日時: {converted_time.strftime('%Y年%m月%d日 %H:%M:%S')}")
    else:
        try:
            url=f"https://api.frankfurter.app/latest?from={from_currency}&to={to_currency}"
            response=requests.get(url,timeout=10)
            if response.status_code==200:
                data=response.json()
                rates=data.get("rates",{})
                if to_currency in rates:
                    rate=rates[to_currency]
                    result=amount*rate
                    converted_time=datetime.now()
                    st.success(f"{amount:,.2f} {from_currency} = {result:,.2f} {to_currency}")
                    st.info(f"為替レート: 1 {from_currency} = {rate:,.6f} {to_currency}")
                    st.info(f"変換日時: {converted_time.strftime('%Y年%m月%d日 %H:%M:%S')}")
                else:
                    st.error("選択した通貨の為替レートを取得できませんでした。")
            else:
                st.error("為替レートの取得に失敗しました。")
        except requests.exceptions.RequestException:
            st.error("APIに接続できませんでした。インターネット接続を確認してください。")
st.divider()
st.subheader("為替レートのグラフ")
period=st.selectbox("グラフの期間",["一週間","一ヶ月","三ヶ月","十二ヶ月"])
days={"一週間":7,"一ヶ月":30,"三ヶ月":90,"十二ヶ月":365}[period]
start_date=datetime.now()-timedelta(days=days)
end_date=datetime.now()
try:
    if from_currency==to_currency:
        dates=pd.date_range(start=start_date.date(),end=end_date.date(),freq="D")
        chart_data=pd.DataFrame({"レート":[1.0]*len(dates)},index=dates)
    else:
        url=f"https://api.frankfurter.app/{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}?from={from_currency}&to={to_currency}"
        response=requests.get(url,timeout=15)
        if response.status_code==200:
            data=response.json()
            rates=data.get("rates",{})
            chart_dates=[]
            chart_rates=[]
            for date,value in sorted(rates.items()):
                if to_currency in value:
                    chart_dates.append(pd.to_datetime(date))
                    chart_rates.append(value[to_currency])
            if chart_dates:
                chart_data=pd.DataFrame({"レート":chart_rates},index=chart_dates)
            else:
                chart_data=pd.DataFrame()
        else:
            chart_data=pd.DataFrame()
    if not chart_data.empty:
        st.line_chart(chart_data)
        latest_rate=float(chart_data["レート"].iloc[-1])
        highest_rate=float(chart_data["レート"].max())
        lowest_rate=float(chart_data["レート"].min())
        col1,col2,col3=st.columns(3)
        with col1:
            st.metric("最新レート",f"{latest_rate:.6f}")
        with col2:
            st.metric("期間中の最高値",f"{highest_rate:.6f}")
        with col3:
            st.metric("期間中の最低値",f"{lowest_rate:.6f}")
        st.subheader("為替レートのデータ")
        display_data=chart_data.copy()
        display_data.index=display_data.index.strftime("%Y年%m月%d日")
        display_data.columns=["為替レート"]
        st.dataframe(display_data,use_container_width=True)
        st.caption(f"1 {from_currency} = {latest_rate:.6f} {to_currency}")
    else:
        st.warning("この通貨の過去の為替データを取得できませんでした。")
except requests.exceptions.RequestException:
    st.error("過去の為替データを取得できませんでした。")
except Exception as e:
    st.error(f"データの処理中にエラーが発生しました: {e}")
st.divider()
st.subheader("最終確認")
check_time=datetime.now()
st.write(f"このページを確認した日時: {check_time.strftime('%Y年%m月%d日 %H:%M:%S')}")
st.write(f"自動更新: {'有効' if auto_refresh else '無効'}")
if auto_refresh:
    st.write(f"{refresh_seconds}秒ごとにページを更新します。")