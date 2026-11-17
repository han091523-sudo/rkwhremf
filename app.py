"""문자수사대 — 로그인/API/DB 없이 실행하는 문자 대응 연습.
실행: streamlit run app.py
진행 기록은 현재 접속에서만 유지됩니다. 모든 메시지는 가상 상황입니다.
"""
import html
import streamlit as st

CASES = [
 {"name":"택배의 함정", "icon":"📦", "sender":"택배 안내 · 가상 상황", "intro":"기다리던 택배가 있는데 문자가 왔다.", "rounds":[
  {"text":"[배송 안내] 주소가 정확하지 않아 배송이 중단됐습니다. 오늘 안에 주소를 수정해 주세요.\n주소 수정: parcel-check.example", "options":["문자의 주소 수정 링크를 누른다","문자는 닫고, 직접 택배사 공식 앱을 연다","급하니까 집 주소부터 답장한다"], "safe":1, "feedback":["급하게 느껴져도 문자 속 링크로 들어가지 않는 연습을 해봐요.","좋아요. 문자에 있는 경로가 아니라 직접 연 공식 앱에서 운송장과 배송 상태를 확인해요.","확인되지 않은 상대에게 집 주소를 보내지 않아요."], "clue":"‘오늘 안에’라는 재촉과 문자 속 외부 링크. 이것만으로 사기를 확정할 수는 없지만 별도 확인이 필요해요."},
  {"text":"연습 상황: 직접 연 공식 앱에서는 배송이 정상 진행 중이다. 그런데 같은 번호에서 ‘배송 재개 수수료 900원을 결제하세요’라는 문자가 또 왔다.", "options":["작은 돈이니까 카드 정보를 넣는다","문자에 적힌 번호로 전화한다","공식 앱의 고객센터로 사실을 확인한다"], "safe":2, "feedback":["소액이라도 카드 정보를 입력하게 만드는 미끼일 수 있어요.","의심 문자에 적힌 번호도 상대가 운영할 수 있어요.","맞아요. 직접 찾은 공식 고객센터로 확인하고 의심 문자의 결제 요청에는 응하지 않아요."], "clue":"공식 앱의 배송 상태와 다른 주장, 추가 결제 요구를 함께 살펴봐요."}]},
 {"name":"진짜 우리 가족?", "icon":"👨‍👩‍👧", "sender":"처음 보는 번호 · 가상 상황", "intro":"낯선 번호가 가족이라고 말한다.", "rounds":[
  {"text":"엄마 나 휴대폰 고장 났어. 지금 임시 번호야. 급한 일 있으니까 여기로 답장해 줘.", "options":["원래 저장된 가족 번호로 전화해 확인한다","가족이라니까 바로 믿는다","이 번호를 가족 이름으로 저장한다"], "safe":0, "feedback":["좋아요. 기존에 알고 있던 연락 수단으로 본인인지 따로 확인해요. 연결되지 않는다고 새 번호를 믿어서는 안 돼요.","가족을 부르는 말만으로는 본인임을 확인할 수 없어요.","확인하기 전에 번호를 바꾸면 나중에도 혼동할 수 있어요."], "clue":"새 번호, 고장 났다는 설명, 급하다는 요청은 별도로 본인 확인을 해야 할 신호예요."},
  {"text":"연습 상황: 아직 가족과 통화하지 못했다. 상대가 ‘통화는 안 돼. 내가 보내는 앱 설치하고 문자로 온 인증번호 좀 알려줘’라고 한다.", "options":["설치만 해 보고 결정한다","설치·인증번호 전달을 멈추고 다른 가족에게도 확인한다","인증번호만 보내 준다"], "safe":1, "feedback":["출처가 확인되지 않은 앱 설치는 기기와 정보에 위험을 줄 수 있어요.","맞아요. 확인 전에는 설치나 정보 전달을 멈추고, 별도로 알고 있던 연락처를 이용해 확인해요.","인증번호는 계정 접근이나 거래 승인에 이용될 수 있으니 다른 사람에게 전달하지 않아요."], "clue":"통화를 피하면서 앱 설치나 인증번호를 요구하는 부분이 핵심이에요."}]},
 {"name":"돌려준다는 돈", "icon":"💸", "sender":"환급 안내 · 가상 상황", "intro":"예상하지 못한 환급 안내가 도착했다.", "rounds":[
  {"text":"[환급 알림] 미수령 환급금이 있습니다. 오늘 신청하지 않으면 소멸됩니다. refund-now.example 에서 확인하세요.", "options":["직접 찾은 해당 기관 공식 홈페이지에서 확인한다","문자의 링크에서 계좌를 입력한다","친구에게도 링크를 보내 준다"], "safe":0, "feedback":["좋아요. 실제 환급 대상인지는 문자 링크가 아니라 공식 경로에서 확인해요.","예상하지 못한 돈을 미끼로 정보를 요구할 수 있어요.","확인되지 않은 링크를 공유하면 다른 사람도 위험에 노출될 수 있어요."], "clue":"예상하지 못한 금전 혜택과 촉박한 마감, 외부 링크를 함께 살펴봐요."},
  {"text":"연습 상황: 공식 경로에서 확인되지 않은 상태다. 상대가 ‘환급 처리를 위해 먼저 보증금을 입금하고 신분증 사진을 보내세요’라고 한다.", "options":["보증금부터 보낸다","신분증만 보낸다","송금과 정보 전달을 멈추고 공식 기관에 확인한다"], "safe":2, "feedback":["돈을 돌려준다는 말로 선입금을 요구할 때는 응하지 말고 별도로 확인해요.","신분증 사진은 민감한 개인정보예요. 확인되지 않은 상대에게 보내지 않아요.","맞아요. 송금·개인정보 전달을 멈추고 직접 찾은 공식 연락처로 확인해요."], "clue":"환급을 조건으로 먼저 돈이나 신분증을 요구하는 부분을 놓치지 마세요."}]}
]

def reset(case):
    st.session_state.case = case
    st.session_state.turn = 0
    st.session_state.answers = []
    st.session_state.choice = None
    st.session_state.page = "play"

def main():
    st.set_page_config(page_title="문자수사대", page_icon="🕵️", layout="centered", initial_sidebar_state="collapsed")
    _ui = st.markdown('''<style>
    .stApp{background:#FFF8EC;color:#20304A}.block-container{max-width:680px;padding:1.5rem 1rem 3rem}
    [data-testid="stSidebar"]{display:none}h1,h2,h3{color:#20304A}
    .stButton button{min-height:54px;border-radius:16px;border:2px solid #20304A;font-weight:700}
    .stButton button[kind="primary"]{background:#5D4BE8;border-color:#5D4BE8;color:white}
    .hero{background:#FFCE60;border:3px solid #20304A;border-radius:26px;padding:24px;margin:12px 0 20px;box-shadow:5px 5px 0 #20304A}
    .hero h1{margin:0;font-size:34px}.hero p{margin:8px 0 0}
    .bubble{background:white;border:2px solid #CCD5E1;border-radius:6px 22px 22px;padding:22px;font-size:19px;line-height:1.8;white-space:pre-wrap;overflow-wrap:anywhere;margin:14px 0 22px}
    .sender{font-weight:bold;color:#485675}.tag{background:#E8E3FF;border-radius:12px;padding:8px 14px;display:inline-block}
    @media(max-width:520px){.hero h1{font-size:28px}.bubble{font-size:18px}.block-container{padding-top:1rem}}
    </style>''', unsafe_allow_html=True)
    if "page" not in st.session_state:
        st.session_state.page = "home"
    _ui = st.markdown("**🕵️ 문자수사대**")
    if st.session_state.page == "home":
        _ui = st.markdown('<div class="hero"><h1>누르기 전에, 잠깐!</h1><p>수상한 문자 속 함정을 찾는 1분 수사 게임</p></div>', unsafe_allow_html=True)
        _ui = st.write("도전할 사건을 골라 주세요.")
        for i,c in enumerate(CASES):
            if st.button(f'{c["icon"]} 사건 {i+1} · {c["name"]}', key=f"case{i}", use_container_width=True):
                _unused = reset(i)
                _ui = st.rerun()
        _ui = st.caption("모든 문자는 가상 연습입니다. 실제 문자의 안전성을 판정하지 않습니다. 링크는 작동하지 않습니다.")
        return
    case = CASES[st.session_state.case]
    if st.button("← 사건 목록"):
        st.session_state.page = "home"
        _ui = st.rerun()
    _ui = st.subheader(case['icon']+' '+case['name'])
    if st.session_state.page == "result":
        score = sum(st.session_state.answers)
        _ui = st.markdown(f'<div class="hero"><h1>수사 완료! {score} / 2</h1><p>점수보다 중요한 건, 다음에 멈춰 확인하는 것!</p></div>', unsafe_allow_html=True)
        for i,r in enumerate(case['rounds']):
            _ui = st.write(f"**장면 {i+1} · {'잘 확인했어요' if st.session_state.answers[i] else '다시 기억해요'}**")
            _ui = st.write(r['clue'])
        _ui = st.info("문자 속 링크·번호 대신, 원래 알고 있던 연락처나 직접 연 공식 앱으로 확인하세요.")
        _ui = st.caption("게임 기록은 현재 접속에서만 유지됩니다.")
        if st.button("이 사건 다시 도전", use_container_width=True):
            _unused = reset(st.session_state.case)
            _ui = st.rerun()
        return
    turn = st.session_state.turn
    r = case['rounds'][turn]
    _ui = st.progress((turn+1)/2, text=f"장면 {turn+1} / 2 · 모든 내용은 연습 상황")
    _ui = st.markdown(f'<div class="sender">{html.escape(case["sender"])}</div><div class="bubble">{html.escape(r["text"])}</div>', unsafe_allow_html=True)
    if st.session_state.choice is None:
        _ui = st.write("**나라면 어떻게 할까?**")
        for j,option in enumerate(r['options']):
            if st.button(option, key=f"option_{st.session_state.case}_{turn}_{j}", use_container_width=True):
                st.session_state.choice = j
                st.session_state.answers.append(j==r['safe'])
                _ui = st.rerun()
    else:
        choice=st.session_state.choice
        _ui = st.write('**내 선택:** '+r['options'][choice])
        if choice==r['safe']:
            _ui = st.success(r['feedback'][choice])
        else:
            _ui = st.warning(r['feedback'][choice])
            _ui = st.write('**더 안전한 선택:** '+r['options'][r['safe']])
        _ui = st.info('🔎 위험 신호 찾기 · '+r['clue'])
        if st.button("다음 장면 →" if turn==0 else "수사 결과 보기 →", type="primary", use_container_width=True):
            if turn==0:
                st.session_state.turn=1
                st.session_state.choice=None
            else:
                st.session_state.page="result"
            _ui=st.rerun()

if __name__ == "__main__":
    _unused=main()
