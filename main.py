import streamlit as st
import pypdf
import io
import itertools
import time

def set_password_and_download(pdf_file, password):
    """PDFファイルにパスワードを設定し、ダウンロード可能なストリームを生成"""
    try:
        reader = pypdf.PdfReader(pdf_file)
        writer = pypdf.PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.encrypt(password)

        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return output_stream

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        return None

def try_password(pdf_stream, password):
    """指定されたパスワードでPDFを開こうと試みる (io.BytesIOを使用)"""
    try:
        pdf_stream.seek(0)  # ストリームの先頭に戻す
        reader = pypdf.PdfReader(pdf_stream)
        if reader.is_encrypted:
            try:
                if reader.decrypt(password):
                    return True
                else:
                    return False
            except:
                return True  # パスワード不要なPDF
    except Exception as e:
        st.error(f"PDFファイルの読み込みエラー: {e}")
        return False

def generate_numeric_passwords(max_length):
    """数字のみのパスワードを生成するジェネレータ"""
    for length in range(1, max_length + 1):
        for combination in itertools.product('0123456789', repeat=length):
            yield ''.join(combination)

def main():
    st.title("PDFユーティリティ:悪用厳禁")
    st.write("ただし、設定／解析できるパスワードは、数字の8桁以下です")

    col1, col2 = st.columns(2)

    with col1:
        st.header("PDFパスワード設定")
        pdf_file_set = st.file_uploader("PDFファイルをアップロード (設定)", type="pdf", key="set_pdf")
        password_set = st.text_input("パスワード (数字のみ、設定)", type="password", key="set_password")

        if pdf_file_set and password_set:
            if not password_set.isdigit():
                st.error("パスワードは数字のみを入力してください。")
            else:
                pdf_stream = set_password_and_download(pdf_file_set, password_set)
                if pdf_stream:
                    st.download_button(
                        label="パスワード付きPDFをダウンロード",
                        data=pdf_stream,
                        file_name="protected.pdf",
                        mime="application/pdf",
                    )

    with col2:
        st.header("PDFパスワード解析")
        pdf_file_crack = st.file_uploader("PDFファイルをアップロード (解析)", type="pdf", key="crack_pdf")

        if pdf_file_crack:
            try:
                # PDFファイルをio.BytesIOオブジェクトとして読み込む
                pdf_stream = io.BytesIO(pdf_file_crack.read())
                reader = pypdf.PdfReader(pdf_stream)

                if not reader.is_encrypted:
                    st.info("パスワードは掛かっていません。")
                else:
                    st.write("解析を開始します...")
                    password_found = False
                    progress_bar = st.progress(0)
                    passwords = list(generate_numeric_passwords(8))
                    total_passwords = len(passwords)
                    start_time = time.time()
                    for i, password in enumerate(passwords):
                        # pdf_stream を try_password に渡す
                        if try_password(pdf_stream, password):
                            st.success(f"パスワードが見つかりました: {password}")
                            password_found = True
                            break
                        progress = (i + 1) / total_passwords
                        progress_bar.progress(progress)
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    st.write(f"解析時間: {elapsed_time:.2f} 秒")
                    if not password_found:
                        st.warning("パスワードが見つかりませんでした。")

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()