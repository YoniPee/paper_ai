import streamlit as st
import io
import json
import zipfile
import google.generativeai as genai

# API 설정
genai.configure(api_key="AIzaSyCsYx7NOvpm-5MQey_Rhc5IVK6WmYE92fY")
model = genai.GenerativeModel("gemini-1.5-flash")

st.title("📁 ZIP 업로드 기반 논문 분석 시스템")

# ZIP 파일 업로드 위젯
uploaded_zip = st.file_uploader(
    "논문 JSON 파일들이 들어있는 ZIP 파일을 업로드하세요:",
    type=["zip"]
)

question = st.text_input("AI에게 물어볼 질문을 입력하세요:")

ask = st.button("질문하기")

if uploaded_zip is not None and question and ask:
    try:
        # ZIP 파일을 메모리에서 열기
        with zipfile.ZipFile(io.BytesIO(uploaded_zip.read())) as z:
            context_list = []
            # ZIP 내부의 모든 파일을 순회하며 .json만 처리
            for name in z.namelist():
                if name.endswith(".json"):
                    with z.open(name) as f:
                        data = json.load(f)
                        sections = data.get("packages", {}) \
                                        .get("gpt", {}) \
                                        .get("sections", {})
                        title = sections.get("title", "")
                        abstract = sections.get("abstract", "")
                        method = sections.get("methodology", "")
                        result = sections.get("results", "")
                        context_list.append(
                            f"📄 제목: {title}\n"
                            f"[초록]\n{abstract}\n"
                            f"[방법론]\n{method}\n"
                            f"[결과]\n{result}\n"
                        )

        if not context_list:
            st.warning("ZIP 파일 안에 .json 논문 파일이 없습니다.")
        else:
            full_context = "\n\n---\n\n".join(context_list)
            prompt = f"""
다음은 여러 논문에서 추출한 핵심 내용입니다. 이 내용을 바탕으로 아래 질문에 답해주세요.

{full_context}

[질문]
{question}
"""
            response = model.generate_content(prompt)
            st.subheader("🧠 AI의 응답:")
            st.write(response.text)

    except Exception as e:
        st.error(f"오류 발생: {str(e)}")
