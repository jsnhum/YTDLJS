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
st.markdown("#### Ladda ner videor och ljud från YouTube direkt till din dator")

# Funktion för att visa YouTube-video
def display_youtube_video(video_id):
    st.video(f"https://www.youtube.com/watch?v={video_id}")

# Funktion för att lista filer i en mapp
def list_files_in_directory(directory_path):
    files = []
    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)
        if os.path.isfile(file_path):
            files.append(file_name)
    return files[0] if files else None

# Funktion för att byta namn på en fil
def rename_file(old_name, new_name):
    os.rename(old_name, new_name)

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
    """Download a YouTube video and return the file path."""
    try:
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
            
            # Make sure the file exists
            if os.path.exists(filename):
                st.success(f"Video nedladdad: {os.path.basename(filename)}")
                return filename
            else:
                # Sometimes the extension might be different, try to find the file
                base_filename = os.path.splitext(filename)[0]
                for ext in ['.mp4', '.webm', '.mkv']:
                    alt_filename = base_filename + ext
                    if os.path.exists(alt_filename):
                        st.success(f"Video nedladdad: {os.path.basename(alt_filename)}")
                        return alt_filename
                
                st.warning(f"Filen verkar ha laddats ner men kan inte hittas: {os.path.basename(filename)}")
                return None
    except Exception as e:
        st.error(f"Det gick inte att ladda ner videon {video_id}: {str(e)}")
        return None

# Funktion för att skapa en nedladdningslänk för en fil
def create_download_link(file_path):
    """Create a download link for a file."""
    try:
        if not file_path or not os.path.exists(file_path):
            st.warning(f"Fil hittades inte: {file_path}")
            return None
            
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > 50:
            return f"<p>⚠️ Filen <b>{os.path.basename(file_path)}</b> är {file_size_mb:.1f} MB och för stor för direktnedladdning via webbläsaren. Kör appen lokalt för att ladda ner stora filer.</p>"
            
        # Read file in smaller chunks to avoid memory issues
        with open(file_path, "rb") as file:
            file_content = file.read()
            
        file_name = os.path.basename(file_path)
        b64 = base64.b64encode(file_content).decode()
        mime_type = "video/mp4" if file_path.endswith(".mp4") else "audio/mpeg" if file_path.endswith(".mp3") else "application/octet-stream"
        href = f'<a href="data:{mime_type};base64,{b64}" download="{file_name}" style="display: inline-block; padding: 0.5rem 1rem; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; margin: 0.5rem 0;">⬇️ Ladda ner {file_name} ({file_size_mb:.1f} MB)</a>'
        return href
    except Exception as e:
        st.error(f"Fel vid skapande av nedladdningslänk för {os.path.basename(file_path)}: {str(e)}")
        return None

# Funktion för att ladda ner ljud med angiven FFmpeg-sökväg
def download_audio_with_ffmpeg(video_id, output_path, output_format='mp3', ffmpeg_path=None):
    try:
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
        
        # Ange specifik FFmpeg-plats om tillgänglig
        if ffmpeg_path and os.path.exists(ffmpeg_path):
            ffmpeg_dir = os.path.dirname(ffmpeg_path)
            ydl_opts['ffmpeg_location'] = ffmpeg_dir
            st.info(f"Använder FFmpeg från: {ffmpeg_dir}")
            
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            title = info.get('title', video_id)
            file_path = os.path.join(output_path, f"{title}.{output_format}")
            
        st.success(f"Ljud nedladdat: {title}.{output_format}")
        return file_path
    except Exception as e:
        st.error(f"Det gick inte att ladda ner ljudet från {video_id}: {str(e)}")
        return None

# Skapa flikar för olika funktioner
tab1, tab2, tab3 = st.tabs(["Visa video", "Ladda ner en video", "Ladda ner flera videor"])

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
        
        # FFmpeg-sökväg
        ffmpeg_path = st.text_input("FFmpeg-sökväg (lämna tom för standardsökväg)", 
                                  help="Exempel: C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe på Windows eller /usr/bin/ffmpeg på Linux/Mac")
        
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
            
            # Konfigurera FFmpeg-sökväg om angiven
            if ffmpeg_path and os.path.exists(ffmpeg_path):
                os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)
                st.success(f"Använder FFmpeg från: {ffmpeg_path}")
                
            if download_type == "Video":
                with st.spinner("Laddar ner video..."):
                    file_path = download_video(video_id_input, output_dir)
                    if file_path:
                        download_link = create_download_link(file_path)
                        st.markdown(download_link, unsafe_allow_html=True)
            else:
                with st.spinner("Laddar ner ljud..."):
                    # Skapa specialanpassade alternativ för ljud med FFmpeg-sökväg
                    if ffmpeg_path and os.path.exists(ffmpeg_path):
                        file_path = download_audio_with_ffmpeg(video_id_input, output_dir, audio_format, ffmpeg_path)
                    else:
                        file_path = download_audio(video_id_input, output_dir, audio_format)
                    
                    if file_path:
                        download_link = create_download_link(file_path)
                        st.markdown(download_link, unsafe_allow_html=True)

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
            
            for i, video_id in enumerate(video_id_list):
                status_text.text(f"Laddar ner video {i+1} av {len(video_id_list)}: {video_id}")
                download_video(video_id, output_dir)
                progress_bar.progress((i + 1) / len(video_id_list))
                time.sleep(1)  # Liten paus mellan nedladdningar
                
            status_text.text("Alla nedladdningar är klara!")

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

**Om du får fel relaterat till FFmpeg:**
1. Du behöver installera FFmpeg för att kunna ladda ner ljud.
2. Ladda ner FFmpeg från [ffmpeg.org](https://ffmpeg.org/download.html)
3. När du installerat FFmpeg, ange sökvägen till ffmpeg.exe i "Avancerade inställningar".
   - Windows: Vanligtvis `C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe`
   - macOS: Oftast `/usr/local/bin/ffmpeg` om installerat via Homebrew
   - Linux: Oftast `/usr/bin/ffmpeg`
""")
