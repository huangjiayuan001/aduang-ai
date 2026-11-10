import streamlit as st
from openai import OpenAI

# 1. 网页基本设置（这俩必须放在最上面）
st.set_page_config(page_title="阿黄的 AI 客服", page_icon="🛵")
st.title("📂 骑手阿黄的智能文件问答助手")

# 2. 连接 AI (填你自己的 Key)
client = OpenAI(
    api_key="sk-6e504afcace24d36bfec26f0c0041a02", 
    base_url="https://api.deepseek.com"
)

# 3. 左侧边栏：清空聊天按钮
if st.sidebar.button("🧹 清空当前聊天记录"):
    st.session_state.messages = [] # 清空记忆
    st.rerun() # 刷新页面

# 4. 网页上传文件按钮
# 在主页面放一个清空按钮
if st.button("🧹 清空聊天记录"):
    st.session_state.messages = [] # 把记忆清空
    st.rerun() # 刷新页面
uploaded_file = st.file_uploader("请上传你的规则文件 (.txt)", type=["txt"])

# 5. 判断：如果没传文件，给个提示
if uploaded_file is None:
    st.info("👆 请先在上方上传一份你的 .txt 规则文件，AI 才能开始工作哦！")

# 6. 如果上传了文件，就开始工作！
if uploaded_file is not None:
    rules_content = uploaded_file.read().decode("utf-8")
    
    # 初始化记忆库
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": f"你是一个外卖平台客服。请严格根据以下资料回答问题。如果资料里有矛盾的规则请指出。\n\n资料：\n{rules_content}"}
        ]
        
    # 显示历史对话
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # 提问输入框
    if prompt := st.chat_input("输入你想问文档里的问题："):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 发送给 AI
        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=st.session_state.messages,
                stream=True
            )
            
            def generate_text():
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                        
            full_response = st.write_stream(generate_text())
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})