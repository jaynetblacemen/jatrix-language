import tkinter as tk
from tkinter import messagebox, filedialog
import os
from groq import Groq


groq_api_key = 'Your_API_KEY'

def execute_user_code(user_text):
    try:
        client = Groq(api_key=groq_api_key)
        completion = client.chat.completions.create(
            model="qwen-2.5-coder-32b",
            messages=[{'role': 'user', 'content': f'Only provide the corrected Python code without any explanation or extra text. Here is the prompt: {user_text}'}],
            temperature=0.6,
            max_completion_tokens=4096,
            top_p=0.95,
            stream=True,
            stop=None,
        )

        generated_code = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:  # Ensure content exists
                generated_code += chunk.choices[0].delta.content

        if not generated_code.strip():
            messagebox.showerror('Error', 'No code was generated. Please try again.')
            return

        # Try to find the actual code by attempting to compile each line
        code_lines = []
        for line in generated_code.split('\n'):
            try:
                compile(line, '<string>', 'exec')
                code_lines.append(line)  # If compilation succeeds, keep the line
            except SyntaxError:
                continue  # Skip non-code lines

        filtered_code = '\n'.join(code_lines)

        if not filtered_code.strip():
            messagebox.showerror('Error', 'No valid code found. Please try again.')
            return

        try:
            compile(filtered_code, '<string>', 'exec')
        except SyntaxError as se:
            messagebox.showerror('Syntax Error', f'Syntax error in generated code: {se}')
            return
        except Exception as e:
            messagebox.showerror('Error', f'Failed to compile code: {e}')
            return

        confirmation = messagebox.askyesno('Generated Code', f'The following code was generated:\n\n{filtered_code}\n\nDo you want to execute it?')
        if not confirmation:
            return

        local_scope = {}
        try:
            exec(filtered_code, {}, local_scope)
            result = local_scope.get('result', 'Code executed successfully.')
            messagebox.showinfo('AI Execution Result', str(result))
        except Exception as e:
            messagebox.showerror('Error', f'Failed to execute code: {e}')

    except Exception as e:
        messagebox.showerror('Error', f'Failed to fetch generated code: {e}')


class JatrixApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Jatrix Language')
        self.root.geometry('800x600')

        # Menu Bar
        self.menu_bar = tk.Menu(root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label='Save', command=self.save_file)
        self.file_menu.add_command(label='Save As', command=self.save_file_as)
        self.menu_bar.add_cascade(label='File', menu=self.file_menu)

        self.menu_bar.add_command(label='Run', command=self.process_text)

        root.config(menu=self.menu_bar)

        # Input Text Box (Full Window)
        self.input_box = tk.Text(root, wrap='word')
        self.input_box.pack(fill='both', expand=True)

        self.current_file = None  # To store the current file name

    def process_text(self):
        user_text = self.input_box.get('1.0', tk.END).strip()

        if not user_text:
            messagebox.showwarning('Warning', 'Please enter some text.')
            return

        execute_user_code(user_text)

    def save_file(self):
        if self.current_file:
            with open(self.current_file, 'w') as file:
                file.write(self.input_box.get('1.0', tk.END))
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')])
        if file_path:
            self.current_file = file_path
            with open(file_path, 'w') as file:
                file.write(self.input_box.get('1.0', tk.END))


if __name__ == '__main__':
    root = tk.Tk()
    app = JatrixApp(root)
    root.mainloop()
















