import streamlit as st
import openai
import requests
import py3Dmol
import pandas as pd

# 📌 페이지 설정 (가장 처음에 호출해야 함)
st.set_page_config(layout="wide")

# 🌟 OpenAI API 키 입력받기
st.sidebar.title("약8이")
api_key = st.sidebar.text_input("🔑 OpenAI API 키를 입력하세요", type="password")

# 페이지 선택
page = st.sidebar.radio("페이지 선택", ["기본정보", "데이터 예측", "3D 구조 예측", "질병 기반 조회"])

# ---------------------- 페이지 1: 기본정보 ----------------------
if page == "기본정보":
    st.title("B-cell epitope 예측 프로그램")
    user_input = st.text_input("GPT API를 이용한 질문창", placeholder="예: 'PPSSPTHDPPDSDP 에피토프 서열의 화학적 특성과 관련 질병은 무엇인가요?'")

    if st.button("출력"):
        if not user_input.strip():
            st.warning("질문을 입력하세요!")
        else:
            with st.spinner("GPT에게 물어보는 중..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "당신은 면역학 및 생물정보학 전문가입니다. 사용자가 입력한 에피토프 서열(예: PPSSPTHDPPDSDP)에 대해 다음 내용을 포함하여 전문적으로 설명하세요:\n\n"
                                    "1. 이 에피토프가 알려진 질병(예: 바이러스, 암 등)과 관련이 있다면 명확히 밝혀주세요.\n"
                                    "2. 이 서열에 포함된 아미노산의 화학적 특성(예: 소수성, 친수성, 전하 등)을 기반으로, 면역반응 유도에 어떤 특성을 가질 수 있는지 설명해주세요.\n"
                                    "3. 이 에피토프가 백신, 진단키트, 항체 개발 등 면역학적 활용 측면에서 어떤 의미가 있는지 정리해주세요.\n"
                                    "4. 가능한 경우 참고될 수 있는 바이러스 이름, 질환명, 면역세포 반응 유형(T세포/B세포 등)을 명시해주세요."
                                )
                            },
                            {"role": "user", "content": user_input}
                        ]
                    )
                    answer = response.choices[0].message.content
                    st.success("🧬 GPT의 응답:")
                    st.markdown(answer)

                    st.markdown("### 📌 추가 정보")
                    st.info("필요한 경우 PubMed나 IEDB 같은 데이터베이스에서 추가 실험적 정보를 확인해보세요.")
                except Exception as e:
                    st.error(f"에러 발생: {e}")


# ---------------------- 페이지 2: 데이터 예측 ----------------------
elif page == "데이터 예측":
    st.title("에피토프 - 안티젠 기반 예측 및 시각화")
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        epitope_input = st.text_input("🧬 에피토프 입력창", placeholder="예: SLLPAIVEL")
    with col2:
        antigen_input = st.text_input("🧪 안티젠 입력창", placeholder="예: spike glycoprotein")
    with col3:
        predict_button = st.button("출력")
    if predict_button:
        if not epitope_input or not antigen_input:
            st.warning("에피토프와 안티젠을 모두 입력하세요.")
        else:
            st.subheader("📊 결과값")
            try:
                mock_result = f"`{epitope_input}` 와 `{antigen_input}`의 예측 점수는 **0.91** 입니다."
                st.write(mock_result)
                prompt = f"에피토프 {epitope_input} 와 안티젠 {antigen_input} 의 상호작용을 시각화한 다이어그램 설명을 생성해줘."
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "당신은 생물정보학 시각화를 돕는 전문가입니다."},
                        {"role": "user", "content": prompt}
                    ]
                )
                gpt_description = response.choices[0].message.content
                st.subheader("🖼 에피토프와 항원에대한 설명")
                st.info(gpt_description)
                epitope_ranges = [{'start': 23, 'end': 30}, {'start': 45, 'end': 50}]
                colors = ['red', 'blue', 'green', 'orange', 'magenta']
                view = py3Dmol.view(query='pdb:2OBD')
                view.setStyle({'cartoon': {'color': 'lightgrey'}})
                for i, epi in enumerate(epitope_ranges):
                    epirange = list(range(epi['start'], epi['end'] + 1))
                    color = colors[i % len(colors)]
                    view.addStyle({'resi': epirange}, {'stick': {'color': color}})
                    view.addLabel(f"Epitope {i+1}", {
                        'position': {'resi': epi['start']},
                        'backgroundColor': color,
                        'fontColor': 'white',
                        'fontSize': 12
                    })
                view.zoomTo()
                html = view._make_html()
                st.components.v1.html(html, height=600)
            except Exception as e:
                st.error(f"예측 중 에러 발생: {e}")

# ---------------------- 페이지 3: 3D 구조 예측 ----------------------
elif page == "3D 구조 예측":
    st.title("🧬 단백질 3D 구조 예측 및 시각화기")
    tab1, tab2 = st.tabs(["🔤 아미노산 서열 입력", "📂 PDB 파일 업로드"])
    def predict_structure(sequence):
        API_URL = "https://api.esmatlas.com/foldSequence/v1/pdb/"
        headers = {"Content-Type": "text/plain"}
        try:
            response = requests.post(
                API_URL,
                data=sequence.encode('utf-8'),
                headers=headers,
                timeout=60
            )
            if response.status_code == 200:
                return response.text
            else:
                st.error(f"❌ 예측 실패 (HTTP 상태 코드: {response.status_code})")
        except requests.exceptions.Timeout:
            st.error("❌ 서버 응답 시간이 초과되었습니다 (504 Gateway Timeout).")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ 요청 중 오류 발생: {e}")
        return None
    def show_structure_from_pdb(pdb_str):
        viewer = py3Dmol.view(width=600, height=400)
        viewer.addModel(pdb_str, "pdb")
        viewer.setStyle({"cartoon": {"color": "spectrum"}})
        viewer.zoomTo()
        return viewer._make_html()
    with tab1:
        sequence = st.text_area("단백질 서열을 입력하세요 (알파벳만, 공백 없이)", height=120)
        if st.button("🧪 구조 예측"):
            if not sequence:
                st.warning("⚠️ 서열을 입력해주세요.")
            else:
                if len(sequence) < 20:
                    st.info("ℹ️ 입력된 서열이 짧으면 구조 예측이 실패할 수 있습니다.")
                with st.spinner("⏳ 구조 예측 중입니다... (최대 1분 소요)"):
                    pdb_data = predict_structure(sequence)
                    if pdb_data:
                        html = show_structure_from_pdb(pdb_data)
                        st.components.v1.html(html, height=500, width=700)
    with tab2:
        uploaded_file = st.file_uploader("🗂 PDB 파일 업로드", type="pdb")
        if uploaded_file:
            pdb_text = uploaded_file.read().decode("utf-8")
            st.success("✅ 파일 업로드 완료")
            html = show_structure_from_pdb(pdb_text)
            st.components.v1.html(html, height=500, width=700)

# ---------------------- 페이지 4: 질병 기반 조회 ----------------------
elif page == "질병 기반 조회":
    st.title("🧬 질병 → 안티젠 → 에피토프 조회")

    def load_data():
        df = pd.read_csv("expanded_disease_antigen_epitope_list.csv")        
        df.columns = df.columns.str.strip()
        df["Disease"] = df["Disease"].fillna("").str.strip()
        df["Antigen"] = df["Antigen"].fillna("").str.strip()
        df["Epitopes"] = df["Epitopes"].fillna("").str.strip()
        return df

    df = load_data()

    # 전체 질병 목록
    disease_list = sorted(df["Disease"].dropna().unique())

    # 질병 선택
    selected_disease = st.selectbox("질병을 선택하세요", disease_list, key="selected_disease")

    if selected_disease:
        # 선택된 질병에 해당하는 안티젠 목록
        antigen_list = sorted(
            df[df["Disease"] == selected_disease]["Antigen"].dropna().unique()
        )
        selected_antigen = st.selectbox("안티젠을 선택하세요", antigen_list, key=f"selected_antigen_{selected_disease}")

        if selected_antigen:
            # 해당 조건으로 필터링
            filtered_df = df[
                (df["Disease"] == selected_disease) &
                (df["Antigen"] == selected_antigen)
            ]
            epitope_strs = filtered_df["Epitopes"].dropna().unique()

            # 쉼표로 분해
            epitopes = [e.strip() for e_str in epitope_strs for e in e_str.split(",") if e.strip()]

            # 출력
            st.markdown("#### 👉 해당 안티젠의 에피토프 목록:")
            if epitopes:
                for epitope in epitopes:
                    st.markdown(f"<div style='font-size:18px; color:#1f77b4;'>{epitope}</div>", unsafe_allow_html=True)
            else:
                st.warning("❗ 에피토프 정보가 없습니다.")

