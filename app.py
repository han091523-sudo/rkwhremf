"""가는 김에 · 실행: streamlit run app.py
GitHub에 이 파일과 requirements.txt 업로드 → Streamlit Community Cloud에서 app.py 배포.
아래 앱 안의 '처음 연결하기'에 데이터베이스 설치 SQL과 Secrets 안내가 있습니다.
각 가족이 같은 전용 가족 계정으로 로그인하는 소규모 가족용 버전입니다.
API 키·비밀번호를 GitHub에 올리지 마세요. 외부 데이터베이스 Supabase 필요.
"""
import datetime as dt
import html
import time
import uuid
import streamlit as st
from supabase import create_client

SQL = '''-- Supabase 프로젝트 SQL Editor에서 실행하세요.
create table if not exists public.family_errands (
 id uuid primary key default gen_random_uuid(),
 owner uuid not null default auth.uid() references auth.users(id),
 title text not null check (char_length(title) between 1 and 80),
 route text not null check (route in ('시내에서','집으로','기숙사로')),
 requester text not null check (char_length(requester) between 1 and 30),
 note text not null default '' check (char_length(note)<=500),
 due date,
 status text not null default '대기' check (status in ('대기','진행','완료')),
 assignee text not null default '' check (char_length(assignee)<=30),
 claim_token uuid,
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now()
);
alter table public.family_errands enable row level security;
drop policy if exists family_private on public.family_errands;
create policy family_private on public.family_errands for all to authenticated
 using (owner=auth.uid()) with check (owner=auth.uid());
grant select, insert, update, delete on public.family_errands to authenticated;
'''
ROUTES=['시내에서','집으로','기숙사로']


def esc(s): return html.escape(str(s))


def config():
    try:return st.secrets.get('SUPABASE_URL',''),st.secrets.get('SUPABASE_ANON_KEY','')
    except Exception:return '', ''


def setup():
    with st.expander('처음 연결하기 · 배포 안내'):
        st.markdown('''**한 번만 설정하면 가족이 각자 휴대폰에서 같은 목록을 봅니다.**

1. Supabase에서 프로젝트를 만들고 SQL Editor에서 아래 SQL을 실행하세요.
2. Authentication → Users에서 **전용 가족 계정**을 만들고 이메일 확인을 완료하세요. 관리 화면에서 Add user로 이메일 확인된 사용자를 생성해도 됩니다.
3. Streamlit Community Cloud에서 GitHub 저장소와 `app.py`를 선택하세요.
4. Streamlit 앱 설정 → Secrets에 아래 두 값을 저장하세요. Supabase의 공개 publishable 키 또는 legacy anon 키를 사용하고, **secret/service_role 키는 사용하지 마세요.**
5. 가족끼리만 전용 계정 이메일과 비밀번호를 안전하게 공유하세요. 각자는 로그인 후 다른 별명을 입력합니다.

이 버전은 가족별 **공동 계정 하나**를 쓰므로 개별 사용자 권한 구분은 없습니다. 별명은 신원 인증이 아니며, 로그인한 가족은 전체 목록을 관리할 수 있어요. 다른 가족은 별도 계정을 써야 목록이 분리됩니다.''')
        st.code('SUPABASE_URL = "https://프로젝트.supabase.co"\nSUPABASE_ANON_KEY = "공개 키"',language='toml')
        st.code(SQL,language='sql')
        st.caption('Supabase 저장 정책과 서비스 이용 조건이 적용됩니다. 주소·암호·결제 정보 등 민감한 내용은 부탁에 적지 마세요. 자동 알림/백그라운드 동기화는 없으며 새로고침 버튼으로 최신 상태를 확인합니다.')


def main():
    st.set_page_config(page_title='가는 김에',page_icon='🛍️',layout='centered',initial_sidebar_state='collapsed')
    st.markdown('''<style>
[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"]{display:none}
.stApp{background:#f6f7fb;color:#192a39}.block-container{max-width:680px;padding:1.5rem 1rem 4rem}
h1,h2,h3{color:#132b39}button{min-height:46px!important;border-radius:14px!important}.stButton>button[kind="primary"]{background:#176b51;border:none;color:white}.hero{background:#123e33;border-radius:25px;padding:26px 24px;color:white;margin-bottom:18px}.hero h1{color:white;font-size:2.15rem;margin:5px 0}.hero p{color:#d5eadf;margin-bottom:0}.pill{font-size:12px;letter-spacing:2px;color:#c5ed8f}.tile{border-left:5px solid #72b48a;background:white;border-radius:15px;padding:18px;margin-top:12px;border:1px solid #e0e6e7}.tile h3{font-size:20px;margin:5px 0 10px}.meta{font-size:13px;color:#566772}.splash{height:70vh;display:flex;align-items:center;justify-content:center;text-align:center}.splashbox{width:100%;background:#123e33;border-radius:35px;padding:65px 15px;color:white}.splashbox h1{color:white}.mark{font-size:70px}
</style>''',unsafe_allow_html=True)
    ss=st.session_state
    if not ss.get('intro'):
        ss.intro=True
        view=st.empty();view.markdown('<div class="splash"><div class="splashbox"><div class="mark">🛍️↗</div><h1>가는 김에</h1><p>부탁은 모으고, 헛걸음은 줄이고.</p></div></div>',unsafe_allow_html=True)
        time.sleep(3);view.empty()
    st.markdown('<div class="hero"><div class="pill">ONE TRIP, TOGETHER</div><h1>가는 김에 🛍️</h1><p>누가 챙기는지 알면, 두 번 살 일 없으니까.</p></div>',unsafe_allow_html=True)
    url,key=config()
    if not url or not key:
        st.info('가족의 부탁을 안전하게 저장하려면 최초 연결이 필요해요. API 키 없이 동작하는 임시 목록으로 가장하지 않습니다.')
        setup();return
    if 'db' not in ss:
        try:ss.db=create_client(url,key)
        except Exception:
            st.error('연결 설정을 확인해 주세요.');setup();return
    db=ss.db
    if not ss.get('logged_in'):
        st.subheader('우리 가족 공간에 들어가기')
        st.caption('가족이 같은 전용 계정으로 로그인하고, 각자의 별명으로 부탁을 맡아요.')
        with st.form('login'):
            email=st.text_input('가족 계정 이메일',max_chars=254)
            password=st.text_input('비밀번호',type='password')
            nick=st.text_input('내 별명',max_chars=30,placeholder='예: 아빠, 엄마, 나')
            enter=st.form_submit_button('함께 챙기러 가기',type='primary',use_container_width=True)
        if enter:
            if not email.strip() or not password or not nick.strip():st.warning('이메일, 비밀번호, 별명을 적어 주세요.')
            else:
                try:
                    auth=db.auth.sign_in_with_password({'email':email.strip(),'password':password})
                    if not auth.user:raise ValueError()
                    ss.logged_in=True;ss.nick=nick.strip();st.rerun()
                except Exception:st.error('로그인하지 못했어요. 계정, 비밀번호, 이메일 확인 상태와 연결 설정을 확인해 주세요.')
        setup();return
    top=st.columns([3,1,1])
    top[0].caption(f'👋 {ss.nick} · 우리 가족 부탁함')
    if top[1].button('새로고침',use_container_width=True):st.rerun()
    if top[2].button('나가기',use_container_width=True):
        try:db.auth.sign_out()
        except Exception:pass
        for k in ('db','logged_in','nick'):ss.pop(k,None)
        st.rerun()
    if ss.get('notice'):st.success(ss.pop('notice'))
    try:items=db.table('family_errands').select('*').order('created_at',desc=True).limit(1000).execute().data
    except Exception:
        st.error('부탁을 불러오지 못했어요. 연결·로그인 만료·데이터베이스 설치를 확인해 주세요. 저장된 데이터를 지우지는 않았어요.');setup();return
    if len(items)==1000:st.warning('최근 1,000건만 표시해요. 오래된 완료 항목을 정리해 주세요.')
    a,b,c=st.columns(3)
    for col,label,status in [(a,'아직 주인 없는 부탁','대기'),(b,'챙기는 중','진행'),(c,'완료했어요','완료')]:col.metric(label,sum(v['status']==status for v in items))
    board,add=st.tabs(['📋 부탁 보기','＋ 부탁 남기기'])
    with add:
        st.subheader('가는 길에 이것도 부탁해요')
        with st.form('add',clear_on_submit=True):
            title=st.text_input('무엇을 챙길까요?',max_chars=80,placeholder='예: 우유 1개, 기숙사에 가져갈 충전기')
            route=st.selectbox('어느 길에?',ROUTES)
            use_due=st.checkbox('필요한 날짜가 있어요')
            due=st.date_input('필요한 날짜',value=dt.date.today())
            note=st.text_area('수량·종류·참고할 점',max_chars=500,placeholder='예: 1L짜리 한 개. 없으면 사지 않아도 돼요.')
            send=st.form_submit_button('부탁 남기기',type='primary',use_container_width=True)
        if send:
            duplicates=[v for v in items if v['status']!='완료' and v['title'].strip().casefold()==title.strip().casefold() and v['route']==route]
            if not title.strip():st.warning('무엇이 필요한지 적어 주세요.')
            elif duplicates:st.warning('같은 이동 경로에 제목이 같은 부탁이 이미 있어요. 목록을 먼저 확인해 주세요. 필요하면 수량을 구분해 작성하세요.')
            else:
                try:
                    db.table('family_errands').insert({'title':title.strip(),'route':route,'requester':ss.nick,'note':note.strip(),'due':str(due) if use_due else None}).execute()
                    ss.notice='부탁을 남겼어요!';st.rerun()
                except Exception:st.error('저장하지 못했어요. 잠시 후 목록을 새로고침해 중복 저장 여부를 확인해 주세요.')
    with board:
        route_filter=st.selectbox('이동 경로',['전체']+ROUTES)
        status_filter=st.radio('어떤 부탁을 볼까요?',['진행할 부탁','내가 맡은 부탁','완료한 부탁'],horizontal=True)
        q=st.text_input('부탁 검색',placeholder='제목이나 메모 검색',max_chars=80).strip().casefold()
        filtered=[v for v in items if (route_filter=='전체' or v['route']==route_filter) and (v['status']=='완료' if status_filter=='완료한 부탁' else v['status']=='진행' and v['assignee']==ss.nick if status_filter=='내가 맡은 부탁' else v['status']!='완료') and (not q or q in (v['title']+' '+v['note']).casefold())]
        if not filtered:st.info('여기는 아직 비어 있어요. 새 부탁을 남기거나 다른 경로를 확인해 보세요.')
        for v in filtered:
            due_text=f' · {v["due"]}까지' if v['due'] else ''
            st.markdown(f'<div class="tile"><div class="meta">{esc(v["route"])} · {esc(v["status"])}{esc(due_text)}</div><h3>{esc(v["title"])}</h3><div class="meta">부탁한 사람: {esc(v["requester"])}'+(f' · 담당: {esc(v["assignee"])}' if v['assignee'] else '')+'</div></div>',unsafe_allow_html=True)
            if v['note']:st.write(v['note'])
            if v['due'] and v['status']!='완료' and v['due']<str(dt.date.today()):st.warning('요청 날짜가 지났어요. 아직 필요한지 확인해 주세요.')
            if v['status']=='대기':
                if st.button('🙋 내가 챙길게',key='claim'+v['id'],type='primary',use_container_width=True):
                    token=str(uuid.uuid4())
                    try:
                        db.table('family_errands').update({'status':'진행','assignee':ss.nick,'claim_token':token,'updated_at':dt.datetime.now(dt.timezone.utc).isoformat()}).eq('id',v['id']).eq('status','대기').execute()
                        check=db.table('family_errands').select('claim_token').eq('id',v['id']).execute().data
                        ss.notice='내가 맡았어요. 다른 가족에게도 담당자가 표시돼요.' if check and check[0]['claim_token']==token else '다른 가족이 먼저 맡았거나 목록이 변경됐어요.'
                        st.rerun()
                    except Exception:st.error('처리 결과를 확인하지 못했어요. 새로고침해 주세요.')
            elif v['status']=='진행' and v['assignee']==ss.nick:
                left,right=st.columns(2)
                for col,label,new_status in [(left,'✓ 챙겼어요','완료'),(right,'다시 부탁하기','대기')]:
                    if col.button(label,key=new_status+v['id'],use_container_width=True):
                        try:
                            change={'status':new_status,'updated_at':dt.datetime.now(dt.timezone.utc).isoformat()}
                            if new_status=='대기':change.update(assignee='',claim_token=None)
                            db.table('family_errands').update(change).eq('id',v['id']).eq('status','진행').eq('claim_token',v['claim_token']).execute()
                            ss.notice='목록을 업데이트했어요. 최신 상태를 확인해 주세요.';st.rerun()
                        except Exception:st.error('처리하지 못했어요. 새로고침해 주세요.')
            with st.expander('부탁 삭제'):
                consent=st.checkbox('가족과 확인했으며 삭제할게요',key='ok'+v['id'])
                if st.button('삭제',key='del'+v['id'],disabled=not consent):
                    try:
                        db.table('family_errands').delete().eq('id',v['id']).execute();st.rerun()
                    except Exception:st.error('삭제하지 못했어요.')
    st.caption('🔄 다른 가족의 변경 내용은 ‘새로고침’으로 확인하세요. 자동 푸시 알림은 없어요. 별명은 서로 다르게 사용해 주세요.')
    with st.expander('우리 가족 사용 약속'):
        st.write('① 필요한 부탁을 남겨요. ② 가는 사람이 먼저 맡아요. ③ 구입·전달이 끝나면 완료해요. 못 하게 되면 다시 부탁하기를 눌러요. 수량이나 경로가 다르면 서로 확인해 주세요.')
        st.caption('이 앱은 이동 경로 최적화나 자동 일정 배정이 아닌, 부탁의 중복·누락을 줄이는 가족 공유 목록입니다.')

if __name__=='__main__':main()
