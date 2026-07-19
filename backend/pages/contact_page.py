"""
Contact form page for user feedback and support
"""

import threading
import json
import urllib.request
import urllib.parse
import customtkinter as ctk
from tkinter import messagebox


class ContactPage(ctk.CTkFrame):
    """Contact form page"""
    
    def __init__(self, parent, get_installation_id_callback, on_back_callback):
        super().__init__(parent)
        self.get_installation_id = get_installation_id_callback
        self.on_back = on_back_callback
        self.submitting = False
        
        self.create_ui()
    
    def create_ui(self):
        """Create the contact form UI"""
        # Header with back button
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))
        
        ctk.CTkButton(header, text="←", width=40, fg_color="transparent", 
            hover_color=("gray75", "gray25"), command=self.on_back).pack(side="left")
        ctk.CTkLabel(header, text="Contact Developer", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left", padx=10)
        
        # Scrollable main content
        main = ctk.CTkScrollableFrame(self)
        main.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Description
        desc_text = "Have questions, suggestions, or feature requests? Send us a message!"
        ctk.CTkLabel(main, text=desc_text, font=ctk.CTkFont(size=13), 
            text_color="gray", wraplength=450).pack(pady=(10, 20))
        
        # Name (Required)
        ctk.CTkLabel(main, text="Name *", font=ctk.CTkFont(size=13, weight="bold"), 
            anchor="w").pack(fill="x", pady=(0, 5))
        self.nama_entry = ctk.CTkEntry(main, height=40, placeholder_text="Enter your name")
        self.nama_entry.pack(fill="x", pady=(0, 15))
        
        # Email (Required)
        ctk.CTkLabel(main, text="Email *", font=ctk.CTkFont(size=13, weight="bold"), 
            anchor="w").pack(fill="x", pady=(0, 5))
        self.email_entry = ctk.CTkEntry(main, height=40, placeholder_text="example@email.com")
        self.email_entry.pack(fill="x", pady=(0, 15))
        
        # Phone (Optional)
        ctk.CTkLabel(main, text="Phone (Optional)", font=ctk.CTkFont(size=13, weight="bold"), 
            anchor="w").pack(fill="x", pady=(0, 5))
        self.phone_entry = ctk.CTkEntry(main, height=40, placeholder_text="+1234567890")
        self.phone_entry.pack(fill="x", pady=(0, 15))
        
        # Type (Dropdown)
        ctk.CTkLabel(main, text="Type *", font=ctk.CTkFont(size=13, weight="bold"), 
            anchor="w").pack(fill="x", pady=(0, 5))
        self.jenis_dropdown = ctk.CTkOptionMenu(main, height=40, 
            values=["Question", "Suggestion", "Feature Request"])
        self.jenis_dropdown.set("Question")
        self.jenis_dropdown.pack(fill="x", pady=(0, 15))
        
        # Message (Required)
        ctk.CTkLabel(main, text="Message *", font=ctk.CTkFont(size=13, weight="bold"), 
            anchor="w").pack(fill="x", pady=(0, 5))
        self.message_textbox = ctk.CTkTextbox(main, height=150)
        self.message_textbox.pack(fill="x", pady=(0, 15))
        
        # Submit button
        self.submit_btn = ctk.CTkButton(main, text="Send Message", height=45, 
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2ecc71", hover_color="#27ae60",
            command=self.submit_form)
        self.submit_btn.pack(fill="x", pady=(10, 0))
        
        # Status label
        self.status_label = ctk.CTkLabel(main, text="", font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=(10, 0))
    
    def validate_email(self, email: str) -> bool:
        """Simple email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def submit_form(self):
        """Submit contact form"""
        if self.submitting:
            return
        
        # Get form values
        nama = self.nama_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        jenis = self.jenis_dropdown.get()
        message = self.message_textbox.get("1.0", "end-1c").strip()
        
        # Validation
        if not nama:
            messagebox.showerror("Error", "Name is required!")
            return
        
        if not email:
            messagebox.showerror("Error", "Email is required!")
            return
        
        if not self.validate_email(email):
            messagebox.showerror("Error", "Invalid email format!")
            return
        
        if not message:
            messagebox.showerror("Error", "Message is required!")
            return
        
        # Disable button and show loading
        self.submitting = True
        self.submit_btn.configure(state="disabled", text="Sending...")
        self.status_label.configure(text="Sending message...", text_color="gray")
        
        # Submit in background thread
        def submit():
            try:
                installation_id = self.get_installation_id()
                
                # Prepare data
                data = {
                    "installation_id": installation_id,
                    "nama": nama,
                    "email": email,
                    "phone": phone if phone else "",
                    "jenis": jenis,
                    "message": message
                }
                
                # Send POST request
                url = "https://api.ytclip.org/webhook/yt-clipper/contact-form"
                json_data = json.dumps(data).encode('utf-8')
                
                req = urllib.request.Request(url, data=json_data, 
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'YT-Short-Clipper'
                    },
                    method='POST')
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status == 200:
                        self.after(0, self.on_submit_success)
                    else:
                        self.after(0, lambda: self.on_submit_error(f"Server error: {response.status}"))
            
            except Exception as e:
                err_msg = str(e)
                self.after(0, lambda msg=err_msg: self.on_submit_error(msg))
        
        threading.Thread(target=submit, daemon=True).start()
    
    def on_submit_success(self):
        """Handle successful submission"""
        self.submitting = False
        self.submit_btn.configure(state="normal", text="Send Message")
        self.status_label.configure(text="✓ Message sent successfully!", text_color="green")
        
        # Clear form
        self.nama_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
        self.jenis_dropdown.set("Question")
        self.message_textbox.delete("1.0", "end")
        
        messagebox.showinfo("Success", "Thank you! Your message has been sent.\nWe will respond shortly.")
    
    def on_submit_error(self, error_msg: str):
        """Handle submission error"""
        self.submitting = False
        self.submit_btn.configure(state="normal", text="Send Message")
        self.status_label.configure(text="✗ Failed to send message", text_color="red")
        
        messagebox.showerror("Error", f"Failed to send message:\n{error_msg}")
