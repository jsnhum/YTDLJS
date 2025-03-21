import streamlit as st
import os
import time
import shutil
import sys
import subprocess
import base64
from yt_dlp import YoutubeDL

st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="📺",
    layout="wide"
)

st.title("YouTube Downloader")
st.markdown("#### Ladda ner videor och ljud från YouTube")

# Funktion för att visa YouTube-video
def display_youtube_video(video_id):
    st.video(f"https://www.youtube.com/watch?v={video_id}")

# Funktion för att lista filer i en mapp
def list_files_in_directory(directory_path):
    files = []
    if os.path.exists(directory_path):
        for file_name in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path):
                files.append(file_name)
    return files

# Funktion för att skapa nedladdningslänk för en fil
def get_download_link(file_path, link_text):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    file_name = os.path.basename(file_path)
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}">{link_text}</a>'
    return href

# Funktion för att uppdatera yt-dlp
def update_ytdlp():
    try:
        st.info("Uppdaterar yt-dlp...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            st.success("yt-dlp har uppdaterats till senaste versionen")
        else:
            st.error(f"Kunde inte uppdatera yt-dlp: {result.stderr}")
    except Exception as e:
        st.error(f"Ett fel uppstod vid uppdatering av yt-dlp: {str(e)}")

# Funktion för att ladda ner YouTube-video
def download_video(video_id, output_path):
    try:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            
        ydl_opts = {
            'format': 'mp4', 
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'no_warnings': False,
            'quiet': False,
            'noplaylist': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'http_headers': {'Referer': 'https://www.youtube.com/'}
        }
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            
        st.success(f"Video nedladdad: {os.path.basename(filename)}")
        return filename
    except Exception as e:
        st.error(f"Det gick inte att ladda ner videon {video_id}: {str(e)}")
        return None

# Funktion för att ladda ner ljud från YouTube-video
def download_audio(video_id, output_path, output_format='mp3'):
    try:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': output_format,
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'nocheckcertificate': True,
            'noplaylist': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'http_headers': {'Referer': 'https://www.youtube.com/'}
        }
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            title = info.get('title', video_id)
            
        expected_filename = f"{title}.{output_format}"
        expected_path = os.path.join(output_path, expected_filename)
        
        st.success(f"Ljud nedladdat: {expected_filename}")
        return expected_path
    except Exception as e:
        st.error(f"Det gick inte att ladda ner ljudet från {video_id}: {str(e)}")
        return None

# Skapa flikar för olika funktioner
tab1, tab2, tab3, tab4 = st.tabs(["Visa video", "Ladda ner en video", "Ladda ner flera videor", "Hantera nedladdade filer"])

# Flik 1: Visa YouTube-video
with tab1:
    st.header("Visa YouTube-video")
    video_id_input = st.text_input("Ange YouTube video-ID:", key="display_video_id")
    
    if st.button("Visa video", key="display_button"):
        if video_id_input:
            display_youtube_video(video_id_input)
        else:
            st.warning("Ange ett video-ID")

# Flik 2: Ladda ner en video eller ljud
with tab2:
    st.header("Ladda ner en video eller ljud")
    
    # Knapp för att uppdatera yt-dlp
    if st.button("Uppdatera yt-dlp till senaste versionen", key="update_yt_dlp"):
        update_ytdlp()
    
    video_id_input = st.text_input("Ange YouTube video-ID:", key="download_video_id")
    output_dir = st.text_input("Ange utdatakatalog (standardvärde: ./downloads):", value="./downloads")
    
    # Avancerade inställningar expander
    with st.expander("Avancerade inställningar"):
        st.info("Om du har problem med nedladdning, prova följande alternativ:")
        use_proxy = st.checkbox("Använd proxy (kan hjälpa vid geografiska begränsningar)")
        if use_proxy:
            proxy_url = st.text_input("Proxy URL (format: http://user:pass@host:port)")
        
        cookies_file = st.file_uploader("Ladda upp en cookies.txt-fil (kan hjälpa vid inloggningsbegränsade videor)", type="txt")
        if cookies_file:
            cookies_path = os.path.join(os.getcwd(), "cookies.txt")
            with open(cookies_path, "wb") as f:
                f.write(cookies_file.getbuffer())
            st.success(f"Cookies-fil sparad: {cookies_path}")
    
    download_type = st.radio("Välj vad du vill ladda ner:", ("Video", "Endast ljud"))
    
    if download_type == "Endast ljud":
        audio_format = st.selectbox("Välj ljudformat:", ["mp3", "wav", "aac", "m4a"])
    
    if st.button("Ladda ner", key="download_button"):
        if not video_id_input:
            st.warning("Ange ett video-ID")
        else:
            # Skapa utdatakatalogen om den inte finns
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            if download_type == "Video":
                with st.spinner("Laddar ner video..."):
                    filename = download_video(video_id_input, output_dir)
                    if filename and os.path.exists(filename):
                        st.markdown(f"**Ladda ner filen:** {get_download_link(filename, 'Klicka här för att ladda ner')}", unsafe_allow_html=True)
            else:
                with st.spinner("Laddar ner ljud..."):
                    filename = download_audio(video_id_input, output_dir, audio_format)
                    if filename and os.path.exists(filename):
                        st.markdown(f"**Ladda ner filen:** {get_download_link(filename, 'Klicka här för att ladda ner')}", unsafe_allow_html=True)

# Flik 3: Ladda ner flera videor
with tab3:
    st.header("Ladda ner flera videor")
    video_ids = st.text_area("Ange YouTube video-IDs (en per rad):")
    output_dir = st.text_input("Ange utdatakatalog (standardvärde: ./downloads):", value="./downloads", key="multi_output_dir")
    
    if st.button("Ladda ner alla", key="download_all_button"):
        if not video_ids:
            st.warning("Ange minst ett video-ID")
        else:
            # Skapa utdatakatalogen om den inte finns
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            video_id_list = [vid.strip() for vid in video_ids.split("\n") if vid.strip()]
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            downloaded_files = []
            for i, video_id in enumerate(video_id_list):
                status_text.text(f"Laddar ner video {i+1} av {len(video_id_list)}: {video_id}")
                filename = download_video(video_id, output_dir)
                if filename:
                    downloaded_files.append(filename)
                progress_bar.progress((i + 1) / len(video_id_list))
                time.sleep(1)  # Liten paus mellan nedladdningar
                
            status_text.text("Alla nedladdningar är klara!")

# Flik 4: Hantera nedladdade filer
with tab4:
    st.header("Hantera nedladdade filer")
    
    output_dir = st.text_input("Sökväg till nedladdningsmapp:", value="./downloads", key="manage_output_dir")
    
    if st.button("Visa filer", key="list_files_button"):
        files = list_files_in_directory(output_dir)
        
        if not files:
            st.info(f"Inga filer hittades i mappen: {output_dir}")
        else:
            st.success(f"Hittade {len(files)} filer:")
            
            file_container = st.container()
            
            with file_container:
                for file in files:
                    file_path = os.path.join(output_dir, file)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB
                    
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"**{file}** ({file_size:.2f} MB)")
                    
                    with col2:
                        st.markdown(get_download_link(file_path, "Ladda ner"), unsafe_allow_html=True)
                    
                    with col3:
                        if st.button("Ta bort", key=f"delete_{file}"):
                            try:
                                os.remove(file_path)
                                st.success(f"Filen '{file}' har tagits bort")
                                st.experimental_rerun()
                            except Exception as e:
                                st.error(f"Kunde inte ta bort filen: {str(e)}")

st.markdown("---")
st.markdown("### Anmärkning")
st.info("""
- För att hitta video-ID:t, titta på webbadressen till YouTube-videon. 
  ID:t är vanligtvis den del som kommer efter `v=` (t.ex. `https://www.youtube.com/watch?v=DETTA_ÄR_ID`).
- Nedladdning av upphovsrättsskyddat material utan tillstånd kan vara olagligt i vissa jurisdiktioner.
- Denna applikation är endast för utbildningssyfte.
""")

st.markdown("### Felsökning")
st.warning("""
**Om du får ett 403 Forbidden-fel:**
1. Klicka på "Uppdatera yt-dlp till senaste versionen" för att se till att du använder den senaste versionen.
2. Vissa videor kan vara begränsade av YouTube och kanske inte går att ladda ner.
3. Prova avancerade inställningar som proxy eller cookies om tillgängligt.
4. Försök igen senare - ibland kan tillfälliga begränsningar förekomma.
""")
