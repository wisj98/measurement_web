import streamlit as st
import hashlib
import pandas as pd
import datetime
from streamlit_modal import Modal
import time

def make_hashes(password):
  return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
  if make_hashes(password) == hashed_text:
    return hashed_text
  return False

# 사용자 정보를 딕셔너리에 저장합니다.
users = {
    "test": make_hashes("1234qwer"), 
}

def app():
  """로그인 기능을 구현하는 함수입니다."""
  st.title("로그인")

  username = st.text_input("사용자 이름")
  password = st.text_input("비밀번호", type='password')
  if st.button("로그인"):
    if username in users and check_hashes(password, users[username]):
      st.success("로그인 성공!")
      st.session_state.logged_in = True
      # 로그인 성공 후 페이지 리디렉션
      st.rerun() 
    else:
      st.error("사용자 이름 또는 비밀번호가 잘못되었습니다.")

def main_page():
    st.title("뭐시기 관리자 페이지")
    df = pd.read_csv("test.csv")
    programs = df['program'].unique().tolist()
    programs.insert(0, "전체")  # 맨 앞에 "전체" 옵션 추가
    selected_program = st.selectbox('program select', programs)

    companies = df['company'].unique().tolist()
    companies.insert(0, "전체")
    selected_company = st.selectbox('company select', companies)

    # session_state 초기화
    if 'filtered_df' not in st.session_state:
        st.session_state.filtered_df = df.copy()  # df를 복사하여 session_state에 저장

    # 데이터프레임 필터링
    if selected_program == "전체":
        st.session_state.filtered_df = df.copy()
    else:
        st.session_state.filtered_df = df[df['program'] == selected_program].copy()
    if selected_company != "전체":
        st.session_state.filtered_df = st.session_state.filtered_df[st.session_state.filtered_df['company'] == selected_company].copy()

    # 필터링된 데이터프레임 출력
    dataframe_placeholder = st.empty() 
    dataframe_placeholder.dataframe(st.session_state.filtered_df)

    col1, col2, col3 = st.columns(3)
    with col1:
        number_input = st.text_input('연장일수(-도 가능)', value="0")
    with col2:
        st.markdown("")
        if st.button(label="연장하기"):
          st.session_state.show_modal = True
    if st.session_state.get("show_modal", False):  # 모달이 열려 있는 상태라면
      modal = Modal(key="", title="정말로 연장하시겠습니까?")
      with modal.container():
        try:
          number_input = int(number_input)
          example = st.session_state.filtered_df.copy()
          example["pre"] = example["until"]
          example["until"] = example["until"].apply(
            lambda x: (datetime.datetime.strptime(x, '%Y/%m/%d').date() + datetime.timedelta(days=number_input)).strftime('%Y/%m/%d')
          )
          example["from_to"] = example.apply(
    lambda row: f'-{row["company"]}의 {row["program"]} 사용 기한을 {row["pre"]}에서 {row["until"]}(으)로 수정합니다.',
    axis=1
)
          st.write("\n\n".join([example.iloc[i]["from_to"] for i in range(len(example))]))
        except:
          st.error("유효한 값을 입력해주세요. ex) 1, 90, -10")

        _col1, _col2 = st.columns(2)
        with _col1:
              if st.button(label="확인"):
                st.session_state.filtered_df = example.copy().drop(columns = ["from_to", "pre"])
                for index, row in st.session_state.filtered_df.iterrows():
                        # 조건: company와 program 컬럼이 동일한 경우
                  matching_index = df[(df['company'] == row['company']) & (df['program'] == row['program'])].index
                  if not matching_index.empty:
                    df.loc[matching_index, 'until'] = row['until']
                    df.to_csv("test.csv", index = False)

                st.session_state.show_modal = False
                st.rerun()
        with _col2:
              if st.button(label="취소"):
                  st.session_state.show_modal = False
                  st.rerun()
    col4, col5 = st.columns(2)
    with col4:
       messages = st.text_input("전달할 메세지를 입력해주세요.")
    with col5:
       st.markdown("")
       if st.button(label="등록"):
          st.session_state.filtered_df["message"] = st.session_state.filtered_df["message"].apply(lambda x: messages)
          print(st.session_state.filtered_df)
          for index, row in st.session_state.filtered_df.iterrows():
                  matching_index = df[(df['company'] == row['company']) & (df['program'] == row['program'])].index
                  if not matching_index.empty:
                    df.loc[matching_index, 'message'] = row['message']
                    df.to_csv("test.csv", index = False)
          st.rerun()

# 앱 실행
if __name__ == '__main__':
  if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

  if st.session_state["logged_in"]:
    main_page()
  else:
    app()