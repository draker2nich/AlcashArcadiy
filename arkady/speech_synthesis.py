import asyncio
import tempfile
import subprocess
import edge_tts

VOICE_DMITRY = "ru-RU-DmitryNeural"
RATE_FAST = "+20%"
VOLUME_NORMAL = "+100%"
PITCH_LOW = "-38Hz"

class TTS:
    def __init__(self, voice=VOICE_DMITRY, rate=RATE_FAST, volume=VOLUME_NORMAL, pitch=PITCH_LOW):
        self.voice = voice
        self.rate = rate
        self.volume = volume
        self.pitch = pitch
    
    def text2speech(self, text):
        asyncio.run(self._speak(text))
    
    async def _speak(self, text):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
            temp_path = tmp.name
        
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, volume=self.volume, pitch=self.pitch)
        await communicate.save(temp_path)
        
        subprocess.run([
            'powershell', '-WindowStyle', 'Hidden', '-Command',
            f'''Add-Type -Name WinMM -Namespace Win32 -MemberDefinition '[DllImport("winmm.dll")] public static extern int mciSendString(string command, System.Text.StringBuilder buffer, int bufferSize, IntPtr hwndCallback);';
            [Win32.WinMM]::mciSendString("open `"{temp_path}`" type mpegvideo alias media", $null, 0, 0);
            [Win32.WinMM]::mciSendString("play media wait", $null, 0, 0);
            [Win32.WinMM]::mciSendString("close media", $null, 0, 0);
            Remove-Item "{temp_path}" -Force;'''
        ], check=False, creationflags=subprocess.CREATE_NO_WINDOW)

if __name__ == "__main__":
    tts = TTS()
    tts.text2speech("Тупорылое уёбище я сосала двум неграм?")