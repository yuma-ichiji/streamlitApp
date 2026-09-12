import streamlit as st
import requests
import pandas as pd
from datetime import datetime,timedelta
import streamlit.components.v1 as components
st.set_page_config(page_title="為替レート変換アプリ",page_icon="💱",layout="wide")
st.title("為替レート変換アプリ")
st.write("最新の為替レートを使って通貨を変換できます。")
currency_names={
    "AED":"UAEディルハム - UAE Dirham",
    "AUD":"豪ドル - Australian Dollar",
    "BGN":"ブルガリア・レフ - Bulgarian Lev",
    "BRL":"ブラジル・レアル - Brazilian Real",
    "CAD":"カナダドル - Canadian Dollar",
    "CHF":"スイスフラン - Swiss Franc",
    "CNY":"中国人民元 - Chinese Yuan",
    "CZK":"チェコ・コルナ - Czech Koruna",
    "DKK":"デンマーク・クローネ - Danish Krone",
    "EUR":"ユーロ - Euro",
    "GBP":"イギリスポンド - British Pound",
    "HKD":"香港ドル - Hong Kong Dollar",
    "HUF":"ハンガリー・フォリント - Hungarian Forint",
    "IDR":"インドネシア・ルピア - Indonesian Rupiah",
    "ILS":"イスラエル・シェケル - Israeli New Shekel",
    "INR":"インド・ルピー - Indian Rupee",
    "ISK":"アイスランド・クローナ - Icelandic Króna",
    "JPY":"日本円 - Japanese Yen",
    "KRW":"韓国ウォン - South Korean Won",
    "MXN":"メキシコ・ペソ - Mexican Peso",
    "MYR":"マレーシア・リンギット - Malaysian Ringgit",
    "NOK":"ノルウェー・クローネ - Norwegian Krone",
    "NZD":"ニュージーランドドル - New Zealand Dollar",
    "PHP":"フィリピン・ペソ - Philippine Peso",
    "PLN":"ポーランド・ズウォティ - Polish Złoty",
    "RON":"ルーマニア・レウ - Romanian Leu",
    "SEK":"スウェーデン・クローナ - Swedish Krona",
    "SGD":"シンガポールドル - Singapore Dollar",
    "THB":"タイ・バーツ - Thai Baht",
    "TRY":"トルコ・リラ - Turkish Lira",
    "USD":"米ドル - US Dollar",
    "ZAR":"南アフリカ・ランド - South African Rand"
}
currencies={}
try:
    currency_response=requests.get("https://api.frankfurter.app/currencies",timeout=10)
    if currency_response.status_code==200:
        api_currencies=currency_response.json()
        preferred_codes=["JPY","USD"]
        for code in preferred_codes:
            if code in api_currencies:
                japanese_name=currency_names.get(code,api_currencies[code])
                currencies[f"{japanese_name} ({code})"]=code
        for code,name in api_currencies.items():
            if code not in preferred_codes:
                japanese_name=currency_names.get(code,name)
                currencies[f"{japanese_name} ({code})"]=code
    else:
        st.error("通貨一覧を取得できませんでした。")
except requests.exceptions.RequestException:
    st.error("通貨一覧を取得できませんでした。")
if not currencies:
    currencies={
        "日本円 - Japanese Yen (JPY)":"JPY",
        "米ドル - US Dollar (USD)":"USD",
        "ユーロ - Euro (EUR)":"EUR"
    }
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
st.divider()
st.subheader("自動更新")
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh=False
auto_refresh=st.checkbox("自動更新する",key="auto_refresh")
refresh_seconds=st.selectbox("更新間隔",[10,30,60,120,300,600],index=0,format_func=lambda x:f"{x}秒")
if st.button("更新",use_container_width=True):
    st.rerun()
st.write(f"自動更新: {'オン' if st.session_state.auto_refresh else 'オフ'}")
if st.session_state.auto_refresh:
    st.write(f"{refresh_seconds}秒ごとに為替情報を更新します。")
st.divider()
st.subheader("通貨変換")
currency_list=list(currencies.keys())
if "from_currency" not in st.session_state:
    st.session_state.from_currency=currency_list[0]
if "to_currency" not in st.session_state:
    st.session_state.to_currency=currency_list[min(1,len(currency_list)-1)]
if st.button("通貨を入れ替える",use_container_width=True):
    st.session_state.from_currency,st.session_state.to_currency=st.session_state.to_currency,st.session_state.from_currency
    st.rerun()
col1,col2=st.columns(2)
with col1:
    from_name=st.selectbox("変換元の通貨",currency_list,index=currency_list.index(st.session_state.from_currency),key="from_currency")
with col2:
    to_name=st.selectbox("変換先の通貨",currency_list,index=currency_list.index(st.session_state.to_currency),key="to_currency")
amount=st.number_input("金額",min_value=0.0,value=1000.0,step=100.0)
from_currency=currencies[from_name]
to_currency=currencies[to_name]
if st.button("変換する",use_container_width=True):
    if from_currency==to_currency:
        converted_time=datetime.now()
        st.success(f"{amount:,.2f} {from_currency} = {amount:,.2f} {to_currency}")
        st.info(f"為替レート: 1 {from_currency} = 1.000000 {to_currency}")
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
st.subheader("電卓")
calc_col1,calc_col2=st.columns(2)
with calc_col1:
    calc_a=st.number_input("計算する数値1",value=0.0,key="calc_a")
with calc_col2:
    calc_b=st.number_input("計算する数値2",value=0.0,key="calc_b")
operation=st.selectbox("計算方法",["足し算","引き算","掛け算","割り算"],key="calc_operation")
if st.button("計算する",use_container_width=True):
    if operation=="足し算":
        calc_result=calc_a+calc_b
        st.success(f"計算結果: {calc_result:,.2f}")
    elif operation=="引き算":
        calc_result=calc_a-calc_b
        st.success(f"計算結果: {calc_result:,.2f}")
    elif operation=="掛け算":
        calc_result=calc_a*calc_b
        st.success(f"計算結果: {calc_result:,.2f}")
    elif operation=="割り算":
        if calc_b==0:
            st.error("0で割ることはできません。")
        else:
            calc_result=calc_a/calc_b
            st.success(f"計算結果: {calc_result:,.2f}")
st.divider()
st.subheader("為替レートのグラフ")
period=st.selectbox("グラフの期間",["7日","30日","90日","365日"],index=1)
days={"7日":7,"30日":30,"90日":90,"365日":365}[period]
run_every=f"{refresh_seconds}s" if st.session_state.auto_refresh else None
@st.fragment(run_every=run_every)
def show_exchange_data():
    st.caption(f"最終確認日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
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
            average_rate=float(chart_data["レート"].mean())
            col1,col2,col3,col4=st.columns(4)
            with col1:
                st.metric("最新レート",f"{latest_rate:.6f}")
            with col2:
                st.metric("最高値",f"{highest_rate:.6f}")
            with col3:
                st.metric("最低値",f"{lowest_rate:.6f}")
            with col4:
                st.metric("平均値",f"{average_rate:.6f}")
            st.subheader("為替レートのデータ")
            display_data=chart_data.copy()
            display_data.index=display_data.index.strftime("%Y年%m月%d日")
            display_data.columns=["為替レート"]
            st.dataframe(display_data,use_container_width=True)
            st.caption(f"1 {from_currency} = {latest_rate:.6f} {to_currency}")
            st.divider()
            st.subheader("レートアラート")
            alert_rate=st.number_input("目標レート",min_value=0.000001,value=150.0,step=0.1,key="alert_rate")
            alert_condition=st.selectbox("アラート条件",["以上になったら","以下になったら"],key="alert_condition")
            alert_triggered=False
            if alert_condition=="以上になったら" and latest_rate>=alert_rate:
                alert_triggered=True
            elif alert_condition=="以下になったら" and latest_rate<=alert_rate:
                alert_triggered=True
            if alert_triggered:
                st.success(f"目標レートを達成しました。現在のレート: {latest_rate:.6f} {to_currency}")
                components.html("""
<script>
const audioContext=new(window.AudioContext||window.webkitAudioContext)();
const oscillator=audioContext.createOscillator();
const gainNode=audioContext.createGain();
oscillator.type="sine";
oscillator.frequency.setValueAtTime(880,audioContext.currentTime);
gainNode.gain.setValueAtTime(0.3,audioContext.currentTime);
oscillator.connect(gainNode);
gainNode.connect(audioContext.destination);
oscillator.start();
oscillator.stop(audioContext.currentTime+0.7);
</script>
""",height=0)
            else:
                st.info(f"目標レート未達成。現在のレート: {latest_rate:.6f} {to_currency}")
        else:
            st.warning("この通貨の過去の為替データを取得できませんでした。")
    except requests.exceptions.RequestException:
        st.error("過去の為替データを取得できませんでした。")
    except Exception as e:
        st.error(f"データの処理中にエラーが発生しました: {e}")
show_exchange_data()
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