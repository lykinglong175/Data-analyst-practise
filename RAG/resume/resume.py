
from google import genai
from google.genai import types


import os

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"] 

client = genai.Client(api_key=GOOGLE_API_KEY)

for m in client.models.list():
    if "embedContent" in m.supported_actions:
        print(m.name)

d1 = """My name is Tony Lan and I am a recent Bachelor of Information Technology graduate from Monash University in Melbourne, Australia, with a strong focus on data analysis and applied machine learning, I can be contacted via mobile at +61 414 187 263 and email at yelan286@gmail.com and I maintain an active online presence on GitHub and LinkedIn where I share projects and learning progress, my professional identity combines data analyst and AI or machine learning engineer skills, meaning I am comfortable taking a problem from raw data through cleaning, exploration, modelling and evaluation all the way to clear visualisations and explanations, my degree gave me a broad IT foundation and I chose to specialise in data pipelines, statistics, model building and software engineering practices around ML, while my self-driven work focuses on real end-to-end projects using Python, pandas, NumPy, scikit-learn and PyTorch, in parallel I work as a Junior Finance Analyst (part-time and remote) at Ykryoku Co., Ltd., where I use SQL and Python to support reconciliation, reporting and dashboarding work, which strengthens my ability to translate messy financial data into clear insights for non-technical stakeholders, and my short-term career goal is to join a professional team as a data analyst or junior ML engineer where I can work with real business data, collaborate with senior engineers, keep building models, and gradually grow into a practitioner who can comfortably switch between discussions about model performance, data quality and business impact while consistently delivering value."""
d2 = """My daily work as a data analyst and AI engineer is centred on Python, where I use pandas and NumPy for manipulating tabular and numerical data, scikit-learn for fast classical machine-learning baselines, and PyTorch for more flexible neural-network experiments, I write queries in SQL to extract, filter, aggregate and join data from relational databases, and I build interactive business dashboards in Power BI so that non-technical stakeholders can explore KPIs and trends, I manage and share code using Git and GitHub with structured repositories that include notebooks, scripts and documentation, I rely on Jupyter Notebook for interactive exploration and Markdown for clear explanations, and my working style is to start with exploratory data analysis to understand distributions, missing values and relationships, then to clean and transform data in a repeatable way, quickly build baseline models and iterate only when they add value, log metrics and visualisations tied to specific code versions, and communicate findings through concise plots and bullet-point summaries so that technical and non-technical teammates can both follow the reasoning and act on the results."""

d3 = """In my Personal AI and Data Lab, which I have run since March 2025 as a self-directed learning environment, I regularly pick datasets from realistic domains such as finance, tabular prediction or images and I treat myself as both data engineer and ML engineer by using pandas and SQL to clean, validate and transform the data, splitting it into training and test sets, then building baseline models in scikit-learn and, when appropriate, neural networks in PyTorch with custom training loops, loss functions and evaluation metrics, and I store each project on GitHub with clear READMEs and experiment notes so others can reproduce and understand my work, while in my part-time remote role as a Junior Finance Analyst at Ykryoku Co., Ltd. since January 2025 I extract financial data from internal systems using SQL, clean and reconcile it in Python and pandas, and then design Power BI dashboards that highlight revenue, expenses, trends and important ratios through intuitive visuals and filters, all while documenting my steps, verifying the numbers against known benchmarks and communicating results in plain language so that managers can trust the data and make informed decisions, and together these personal and professional experiences show that I can handle the full lifecycle of data work from ingestion and cleaning through modelling and evaluation to business-oriented communication."""

documents = [d1, d2, d3]
from chromadb import Documents,EmbeddingFunction,Embeddings
from google.api_core import retry


is_retriable = lambda e:(isinstance(e,genai.errors.APIError) and e.code in{429,503})

class EmbeddingFunction(EmbeddingFunction):
    document_mode = True
    @retry.Retry(predicate=is_retriable)
    def __call__(self,input:Documents) -> Embeddings:
        if self.document_mode:
            embedding_task = "retrieval_document"
        else:
            embedding_task = "retrieval_query"
        response = client.models.embed_content( 
            model = "models/text-embedding-004",
            contents = input,
            config = types.EmbedContentConfig(task_type=embedding_task)
        )
        return [e.values for e in response.embeddings]
import chromadb
db_name = "resume"
embed_fn = EmbeddingFunction()
embed_fn.document_mode = True
chroma_client = chromadb.Client()
db = chroma_client.get_or_create_collection(name=db_name,embedding_function=embed_fn)
db.add(documents=documents,ids=[str(i) for i in range(len(documents))])
embed_fn.document_mode = False

import streamlit as st

@st.cache_resource
def init_rag():
    return db,client




def rag_answer(question: str) -> str:
    """给一个问题，走：检索 -> 拼 prompt -> 调 Gemini，返回答案文本"""
    #  拿到 DB / client（已经写好的初始化函数）
    db, client = init_rag()   # 确保实现了这个函数

    # 2. 用问题去 Chroma检索
    result = db.query(query_texts=[question], n_results=3)
    # chroma 返回的是 list[list[str]]，所以第一个
    passages = result["documents"][0]

    # 3. 拼 prompt
    prompt = build_prompt(question, passages)

    # 4. 调 Gemini 生成答案
    answer = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return answer.text

def build_prompt(query: str, passages: list[str]) -> str:
    query_oneline = query.replace("\n", " ")
    prompt = f"""You are a helpful and informative bot that answers questions using text from the reference passage included below.
Be sure to respond in a complete sentence, being comprehensive, including all relevant background information.
However, you are talking to a non-technical audience, so be sure to break down complicated concepts and
strike a friendly and conversational tone. If the passage is irrelevant to the answer, you may ignore it.

QUESTION: {query_oneline}
"""
    for passage in passages:
        passage_oneline = passage.replace("\n", " ")
        prompt += f"PASSAGE: {passage_oneline}\n"
    return prompt




import streamlit as st

def main():
    st.set_page_config(page_title="Tony Resume Q&A")
    st.title("Tony Resume Q&A (RAG Demo)")

   

    question = st.text_input("Please enter your question to tony  ；） ：")

    if st.button("Ask") and question.strip():
        with st.spinner("Generating answer..."):
            try:
                answer_text = rag_answer(question)
            except Exception as e:
                answer_text = f"调用模型时出错：{e}"

        st.markdown("### Answer：")
        st.write(answer_text)

if __name__ == "__main__":
    main()