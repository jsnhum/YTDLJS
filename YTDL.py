import streamlit as st
import os
import base64
from yt_dlp import YoutubeDL

st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="📺",
    layout="wide"
)

st.title("YouTube Downloader")
st.markdown("#### Ladda ner videor och ljud från YouTube")

# Funktion för att skapa en nedladdningslänk för en fil
def create_download_link(file_path):
    try:
        if not os.path.exists(file_path):
            st.warning(f"Filen hittades inte: {file_path}")
            return None
            
        with open(file_path, "rb") as file:
            file_content = file.read()
            
        file_name = os.path.basename(file_path)
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        if file_size_mb > 100:  # Varning för stora filer
            st.warning(f"Filen är {file_size_mb:.1f} MB, vilket kan ta längre tid att ladda ner.")
            
        b64 = base64.b64encode(file_content).decode()
        mime_type = "video/mp4" if file_path.endswith(".mp4") else "audio/mpeg" if file_path.endswith(".mp3") else "application/octet-stream"
        href = f'<a href="data:{mime_type};base64,{b64}" download="{file_name}" style="display: inline-block; padding: 0.5rem 1rem; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px;">⬇️ Ladda ner {file_name} ({file_size_mb:.1f} MB)</a>'
        return href
    except Exception as e:
        st.error(f"Fel vid skapande av nedladdningslänk: {str(e)}")
        return None

# Funktion för att visa YouTube-video
def display_youtube_video(video_id):
    st.video(f"https://www.youtube.com/watch?v={video_id}")

# Funktion för att ladda ner YouTube-video
def download_video(video_id, output_path):
    try:
        ydl_opts = {
            'format': 'mp4', 
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s')
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
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': output_format,
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        }
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            title = info.get('title', video_id)
            # Skapa fullständig sökväg till den nedladdade ljudfilen
            file_path = os.path.join(output_path, f"{title}.{output_format}")
            
        st.success(f"Ljud nedladdat: {title}.{output_format}")
        return file_path
    except Exception as e:
        st.error(f"Det gick inte att ladda ner ljudet från {video_id}: {str(e)}")
        return None

# Skapa flikar för olika funktioner
tab1, tab2 = st.tabs(["Visa video", "Ladda ner en video"])

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
    video_id_input = st.text_input("Ange YouTube video-ID:", key="download_video_id")
    output_dir = st.text_input("Ange utdatakatalog (standardvärde: ./downloads):", value="./downloads")
    
    download_type = st.radio("Välj vad du vill ladda ner:", ("Video", "Endast ljud"))
    
    if download_type == "Endast ljud":
        audio_format = st.selectbox("Välj ljudformat:", ["mp3", "wav", "aac", "m4a"])
    
    # Container för att visa nedladdningslänk
    download_link_container = st.container()
    
    if st.button("Ladda ner", key="download_button"):
        if not video_id_input:
            st.warning("Ange ett video-ID")
        else:
            # Skapa utdatakatalogen om den inte finns
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            if download_type == "Video":
                with st.spinner("Laddar ner video..."):
                    file_path = download_video(video_id_input, output_dir)
                    if file_path:
                        with download_link_container:
                            st.success("Nedladdning klar! Klicka på länken nedan för att spara filen på din dator:")
                            download_link = create_download_link(file_path)
                            if download_link:
                                st.markdown(download_link, unsafe_allow_html=True)
            else:
                with st.spinner("Laddar ner ljud..."):
                    file_path = download_audio(video_id_input, output_dir, audio_format)
                    if file_path:
                        with download_link_container:
                            st.success("Nedladdning klar! Klicka på länken nedan för att spara filen på din dator:")
                            download_link = create_download_link(file_path)
                            if download_link:
                                st.markdown(download_link, unsafe_allow_html=True)

st.markdown("---")
st.markdown("### Anmärkning")
st.info("""
- För att hitta video-ID:t, titta på webbadressen till YouTube-videon. 
  ID:t är vanligtvis den del som kommer efter `v=` (t.ex. `https://www.youtube.com/watch?v=DETTA_ÄR_ID`).
- Nedladdning av upphovsrättsskyddat material utan tillstånd kan vara olagligt i vissa jurisdiktioner.
- För att ladda ner ljud behöver du ha FFmpeg installerat på din dator.
- Om du kör appen i molnet måste du använda nedladdningslänken för att få filen till din dator.
- Om du kör appen lokalt sparas filerna i den angivna katalogen.
- Denna applikation är endast för utbildningssyfte.
""")

st.markdown("### Tips")
st.success("""
**Om du kör appen i molnet (t.ex. Streamlit Cloud):**
- Filerna laddas först ner till servern och sedan till din dator via nedladdningslänken
- Stora filer kan ta längre tid att ladda ner
- Sessionen i molnet är tillfällig, så filerna sparas inte permanent

**Om du kör appen lokalt:**
- Filerna sparas direkt i den angivna katalogen på din dator
- Du behöver inte använda nedladdningslänken, men den finns tillgänglig
- För att köra lokalt, använd kommandot: `streamlit run app.py`
""")
