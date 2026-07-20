"""
Terms of Service Dialog for YT Short Clipper
Shows bilingual (English + Indonesian) terms that users must accept before using the app.
"""

import customtkinter as ctk
from tkinter import font as tkfont


# ============================================================
# TERMS OF SERVICE TEXT
# ============================================================

TERMS_EN = """TERMS OF SERVICE & DISCLAIMER
YT Short Clipper

Last Updated: February 2026

By using YT Short Clipper ("the Software"), you acknowledge that you have read, understood, and agree to be bound by the following terms and conditions. If you do not agree, you must immediately stop using the Software.

1. NATURE OF THE SOFTWARE

YT Short Clipper is an open-source tool designed to assist users in creating short-form video clips from YouTube content. The Software is provided "AS IS" and "AS AVAILABLE" without warranties of any kind, either express or implied.

2. USER RESPONSIBILITY & COPYRIGHT COMPLIANCE

2.1. You are solely responsible for ensuring that your use of this Software complies with all applicable laws, regulations, and third-party rights, including but not limited to copyright, intellectual property, and privacy laws.

2.2. You must only clip, modify, or redistribute video content for which you have obtained proper authorization from the original content creator or rights holder, OR for which your use qualifies as "fair use" or "fair dealing" under applicable law.

2.3. You acknowledge that downloading, clipping, re-uploading, or otherwise redistributing YouTube content without the explicit permission of the copyright holder may constitute copyright infringement and may violate YouTube's Terms of Service.

2.4. You are fully responsible for verifying that your intended use of any content processed through this Software is lawful and does not infringe upon any third-party rights.

3. DISCLAIMER OF LIABILITY

3.1. The developer(s) and contributor(s) of YT Short Clipper ("the Developers") shall NOT be held liable for any direct, indirect, incidental, special, consequential, or exemplary damages arising from or related to your use of the Software, including but not limited to:
   a) Copyright infringement claims or lawsuits;
   b) Violations of YouTube's Terms of Service;
   c) Violations of any platform's terms of service;
   d) Any legal action taken against you by content creators, rights holders, or any third party;
   e) Loss of revenue, data, or business opportunities;
   f) Any penalties, fines, or sanctions imposed by any authority.

3.2. The Developers do not endorse, encourage, or facilitate copyright infringement or any illegal activity. The Software is intended for lawful use only.

4. INDEMNIFICATION

You agree to indemnify, defend, and hold harmless the Developers from and against any and all claims, damages, obligations, losses, liabilities, costs, and expenses (including attorney's fees) arising from:
   a) Your use of the Software;
   b) Your violation of these Terms;
   c) Your violation of any third-party rights, including copyright;
   d) Any content you create, modify, or distribute using the Software.

5. NO LEGAL ADVICE

Nothing in this Software or its documentation constitutes legal advice. If you are unsure whether your intended use of content is lawful, you should consult a qualified legal professional in your jurisdiction.

6. YOUTUBE TERMS OF SERVICE

You acknowledge that YouTube has its own Terms of Service (https://www.youtube.com/t/terms) that govern the use of content on its platform. You are responsible for complying with YouTube's Terms of Service at all times when using this Software.

7. FAIR USE NOTICE

This Software may be used for purposes that qualify as "fair use" under applicable copyright law, such as commentary, criticism, education, news reporting, or research. However, the determination of whether a particular use qualifies as fair use is a legal determination that depends on the specific circumstances. The Developers make no representation that any particular use of this Software constitutes fair use.

8. MODIFICATIONS TO TERMS

The Developers reserve the right to modify these Terms at any time. Continued use of the Software after any modifications constitutes acceptance of the updated Terms.

9. GOVERNING LAW

These Terms shall be governed by and construed in accordance with the laws applicable in the user's jurisdiction. Any disputes arising from these Terms shall be resolved in the competent courts of the user's jurisdiction.

10. ACCEPTANCE

By clicking "I Agree" or by using the Software, you confirm that:
   a) You have read and understood these Terms in their entirety;
   b) You accept full responsibility for your use of the Software;
   c) You will not hold the Developers liable for any consequences of your use;
   d) You will comply with all applicable laws and third-party rights."""


TERMS_ID = """SYARAT DAN KETENTUAN PENGGUNAAN & PENYANGKALAN
YT Short Clipper

Terakhir Diperbarui: Februari 2026

Dengan menggunakan YT Short Clipper ("Perangkat Lunak"), Anda mengakui bahwa Anda telah membaca, memahami, dan setuju untuk terikat oleh syarat dan ketentuan berikut. Jika Anda tidak setuju, Anda harus segera berhenti menggunakan Perangkat Lunak ini.

1. SIFAT PERANGKAT LUNAK

YT Short Clipper adalah alat open-source yang dirancang untuk membantu pengguna membuat klip video pendek dari konten YouTube. Perangkat Lunak ini disediakan "APA ADANYA" dan "SEBAGAIMANA TERSEDIA" tanpa jaminan dalam bentuk apa pun, baik tersurat maupun tersirat.

2. TANGGUNG JAWAB PENGGUNA & KEPATUHAN HAK CIPTA

2.1. Anda bertanggung jawab sepenuhnya untuk memastikan bahwa penggunaan Perangkat Lunak ini mematuhi semua hukum, peraturan, dan hak pihak ketiga yang berlaku, termasuk namun tidak terbatas pada hukum hak cipta, kekayaan intelektual, dan privasi.

2.2. Anda hanya boleh memotong, memodifikasi, atau mendistribusikan ulang konten video yang telah Anda peroleh izin yang sah dari pembuat konten asli atau pemegang hak, ATAU yang penggunaannya memenuhi syarat sebagai "penggunaan wajar" (fair use) berdasarkan hukum yang berlaku.

2.3. Anda mengakui bahwa mengunduh, memotong, mengunggah ulang, atau mendistribusikan ulang konten YouTube tanpa izin eksplisit dari pemegang hak cipta dapat merupakan pelanggaran hak cipta dan dapat melanggar Ketentuan Layanan YouTube.

2.4. Anda bertanggung jawab sepenuhnya untuk memverifikasi bahwa penggunaan konten yang Anda proses melalui Perangkat Lunak ini adalah sah dan tidak melanggar hak pihak ketiga mana pun.

3. PENYANGKALAN TANGGUNG JAWAB

3.1. Pengembang dan kontributor YT Short Clipper ("Pengembang") TIDAK bertanggung jawab atas segala kerugian langsung, tidak langsung, insidental, khusus, konsekuensial, atau sebagai contoh yang timbul dari atau terkait dengan penggunaan Perangkat Lunak oleh Anda, termasuk namun tidak terbatas pada:
   a) Klaim atau tuntutan pelanggaran hak cipta;
   b) Pelanggaran Ketentuan Layanan YouTube;
   c) Pelanggaran ketentuan layanan platform mana pun;
   d) Tindakan hukum apa pun yang diambil terhadap Anda oleh pembuat konten, pemegang hak, atau pihak ketiga mana pun;
   e) Kehilangan pendapatan, data, atau peluang bisnis;
   f) Denda, sanksi, atau hukuman apa pun yang dijatuhkan oleh otoritas mana pun.

3.2. Pengembang tidak mendukung, mendorong, atau memfasilitasi pelanggaran hak cipta atau aktivitas ilegal apa pun. Perangkat Lunak ini ditujukan hanya untuk penggunaan yang sah.

4. GANTI RUGI

Anda setuju untuk mengganti rugi, membela, dan membebaskan Pengembang dari segala klaim, kerugian, kewajiban, biaya, dan pengeluaran (termasuk biaya pengacara) yang timbul dari:
   a) Penggunaan Perangkat Lunak oleh Anda;
   b) Pelanggaran Anda terhadap Syarat ini;
   c) Pelanggaran Anda terhadap hak pihak ketiga mana pun, termasuk hak cipta;
   d) Konten apa pun yang Anda buat, modifikasi, atau distribusikan menggunakan Perangkat Lunak ini.

5. BUKAN NASIHAT HUKUM

Tidak ada dalam Perangkat Lunak ini atau dokumentasinya yang merupakan nasihat hukum. Jika Anda tidak yakin apakah penggunaan konten yang Anda maksudkan adalah sah, Anda harus berkonsultasi dengan profesional hukum yang berkualifikasi di yurisdiksi Anda.

6. KETENTUAN LAYANAN YOUTUBE

Anda mengakui bahwa YouTube memiliki Ketentuan Layanan sendiri (https://www.youtube.com/t/terms) yang mengatur penggunaan konten di platformnya. Anda bertanggung jawab untuk mematuhi Ketentuan Layanan YouTube setiap saat saat menggunakan Perangkat Lunak ini.

7. PEMBERITAHUAN PENGGUNAAN WAJAR

Perangkat Lunak ini dapat digunakan untuk tujuan yang memenuhi syarat sebagai "penggunaan wajar" (fair use) berdasarkan hukum hak cipta yang berlaku, seperti komentar, kritik, pendidikan, pelaporan berita, atau penelitian. Namun, penentuan apakah penggunaan tertentu memenuhi syarat sebagai penggunaan wajar adalah keputusan hukum yang bergantung pada keadaan spesifik. Pengembang tidak membuat pernyataan bahwa penggunaan tertentu dari Perangkat Lunak ini merupakan penggunaan wajar.

8. PERUBAHAN KETENTUAN

Pengembang berhak untuk mengubah Ketentuan ini kapan saja. Penggunaan Perangkat Lunak yang berkelanjutan setelah perubahan apa pun merupakan penerimaan terhadap Ketentuan yang diperbarui.

9. HUKUM YANG BERLAKU

Ketentuan ini diatur oleh dan ditafsirkan sesuai dengan hukum yang berlaku di yurisdiksi pengguna. Setiap perselisihan yang timbul dari Ketentuan ini akan diselesaikan di pengadilan yang berwenang di yurisdiksi pengguna.

10. PENERIMAAN

Dengan mengklik "Saya Setuju" atau dengan menggunakan Perangkat Lunak ini, Anda mengonfirmasi bahwa:
   a) Anda telah membaca dan memahami Ketentuan ini secara keseluruhan;
   b) Anda menerima tanggung jawab penuh atas penggunaan Perangkat Lunak ini;
   c) Anda tidak akan meminta pertanggungjawaban Pengembang atas konsekuensi apa pun dari penggunaan Anda;
   d) Anda akan mematuhi semua hukum yang berlaku dan hak pihak ketiga."""


class TermsOfServiceDialog(ctk.CTkToplevel):
    """Modal dialog that shows Terms of Service and requires user acceptance."""
    
    def __init__(self, parent, on_accept_callback):
        super().__init__(parent)
        
        self.on_accept = on_accept_callback
        self.accepted = False
        self.current_lang = "en"
        
        # Window setup
        self.title("Terms of Service / Syarat dan Ketentuan")
        self.geometry("700x580")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 350
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 290
        self.geometry(f"+{x}+{y}")
        
        self._build_ui()
    
    def _build_ui(self):
        # Main container
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Header
        header_frame = ctk.CTkFrame(main, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="📜 Terms of Service",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")
        
        # Language toggle
        lang_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        lang_frame.pack(side="right")
        
        self.en_btn = ctk.CTkButton(
            lang_frame, text="English", width=80, height=28,
            font=ctk.CTkFont(size=11),
            fg_color=("#1f538d", "#14375e"),
            command=lambda: self._switch_lang("en")
        )
        self.en_btn.pack(side="left", padx=(0, 5))
        
        self.id_btn = ctk.CTkButton(
            lang_frame, text="Indonesia", width=80, height=28,
            font=ctk.CTkFont(size=11),
            fg_color=("#3a3a3a", "#2a2a2a"),
            command=lambda: self._switch_lang("id")
        )
        self.id_btn.pack(side="left")
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            main,
            text="Please read the following terms carefully before using this application.",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.subtitle_label.pack(fill="x", pady=(0, 8))
        
        # Terms text area
        self.terms_textbox = ctk.CTkTextbox(
            main, width=660, height=380,
            font=ctk.CTkFont(size=12),
            fg_color=("#1a1a1a", "#0a0a0a"),
            border_width=1,
            border_color=("#3a3a3a", "#2a2a2a"),
            wrap="word"
        )
        self.terms_textbox.pack(fill="both", expand=True, pady=(0, 10))
        self.terms_textbox.insert("1.0", TERMS_EN)
        self.terms_textbox.configure(state="disabled")
        
        # Checkbox
        self.agree_var = ctk.BooleanVar(value=False)
        self.agree_check = ctk.CTkCheckBox(
            main,
            text="I have read and agree to the Terms of Service / Saya telah membaca dan menyetujui Syarat dan Ketentuan",
            variable=self.agree_var,
            font=ctk.CTkFont(size=11),
            command=self._on_checkbox_toggle
        )
        self.agree_check.pack(fill="x", pady=(0, 10))
        
        # Buttons
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        self.decline_btn = ctk.CTkButton(
            btn_frame, text="Decline / Tolak", width=140, height=38,
            font=ctk.CTkFont(size=12),
            fg_color=("#6c757d", "#5a6268"),
            hover_color=("#5a6268", "#4e555b"),
            command=self._on_close
        )
        self.decline_btn.pack(side="left")
        
        self.accept_btn = ctk.CTkButton(
            btn_frame, text="I Agree / Saya Setuju", width=200, height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="gray", hover_color="gray",
            state="disabled",
            command=self._on_accept
        )
        self.accept_btn.pack(side="right")
    
    def _switch_lang(self, lang: str):
        self.current_lang = lang
        
        # Update button styles
        active_color = ("#1f538d", "#14375e")
        inactive_color = ("#3a3a3a", "#2a2a2a")
        
        if lang == "en":
            self.en_btn.configure(fg_color=active_color)
            self.id_btn.configure(fg_color=inactive_color)
            self.subtitle_label.configure(
                text="Please read the following terms carefully before using this application."
            )
        else:
            self.en_btn.configure(fg_color=inactive_color)
            self.id_btn.configure(fg_color=active_color)
            self.subtitle_label.configure(
                text="Harap baca syarat dan ketentuan berikut dengan seksama sebelum menggunakan aplikasi ini."
            )
        
        # Update text content
        self.terms_textbox.configure(state="normal")
        self.terms_textbox.delete("1.0", "end")
        self.terms_textbox.insert("1.0", TERMS_EN if lang == "en" else TERMS_ID)
        self.terms_textbox.configure(state="disabled")
    
    def _on_checkbox_toggle(self):
        if self.agree_var.get():
            self.accept_btn.configure(
                state="normal",
                fg_color=("#27ae60", "#219a52"),
                hover_color=("#219a52", "#1a7a40")
            )
        else:
            self.accept_btn.configure(
                state="disabled",
                fg_color="gray",
                hover_color="gray"
            )
    
    def _on_accept(self):
        self.accepted = True
        self.grab_release()
        self.destroy()
        if self.on_accept:
            self.on_accept()
    
    def _on_close(self):
        """User declined or closed the dialog — exit the app."""
        self.accepted = False
        self.grab_release()
        self.destroy()
        # Quit the entire application
        self.master.destroy()
