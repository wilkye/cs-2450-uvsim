# UVSim - BasicML Virtual Machine

## 📖 Description
UVSim is a program that lets you run and watch simple programs written in a very basic computer language. It helps you see step by step how a tiny "toy computer" works by showing what happens inside as the program runs.

---

## ⚙️ Prerequisites
- Python **3.8+**
- Command-line access

---

## 🚀 How to Run
1. Open a terminal and navigate to the project folder.  
2. Run the simulator by typing:  
   ```bash
   python main.py
   ```  
3. **Opening a File:**  
   - **Mac:** Click “File” in the menu bar near the Apple logo → click **Open** → select a program file (e.g., `Test6.txt`).  
   - **Windows:** Click “File” at the top left corner → click **Open** → select a program file (e.g., `Test6.txt`).  
   - If you select an invalid file, the Output/Log box will display an error message.  
4. Press the **Run** button to execute the program. You will see updates in the output area and may be prompted to type input values as the program runs.

---

## 💾 File Saving
You can now save your current program or memory state directly from the interface:  
- Click **File → Save (or save as)** to store the current state of your loaded or edited program.  
- You’ll be prompted to choose a destination and filename for saving.  
- Saved files can later be reopened with **File → Open**.

---

## 🧠 Memory Editing
UVSim now supports direct memory editing:  
- **Double-click** on any memory cell in the memory table to edit its value.  
- Press **Enter** to confirm your change.  
- You can also **clear selected memory entries** to customize your program or test memory behavior interactively.

---

## 🎨 Custom Color Themes
You can personalize UVSim’s appearance with system-wide custom colors **(File → Themes)**:  
- Change background, text, and highlight colors to fit your preferences.  
- These color settings apply across the entire application for a consistent and accessible look.

---

## 🪟 Multiple Instances Support

UVSim now supports running multiple simulator windows at the same time.
You can open a completely new instance by selecting:

**File → Open New Window**

Each window runs independently, allowing you to test different programs, compare outputs, or debug side-by-side without interfering with your main session.

---

## 💡 What You'll See
While the program is running, you will see messages that tell you what the simulator is doing—such as loading instructions, reading input, or displaying output. You might also see updates showing the contents of memory or the accumulator (a special place where calculations happen).  

Example output:
```
Enter an integer: 123
Stored 123 at memory location 10
Accumulator updated to +0123
Program halted successfully.
```

---

## 📥 Input Instructions
When the program requests input:
- Type a number (positive or negative) into the bottom text box and press Enter.  
- Enter one number at a time as prompted.

Example:
```
25
-10
0
```

---

## 🖥 Instruction Set (Reference)

| Code | Mnemonic    | Description |
|------|-------------|-------------|
| 10   | READ        | Read a word from keyboard into memory |
| 11   | WRITE       | Write a word from memory to screen |
| 20   | LOAD        | Load a word from memory into accumulator |
| 21   | STORE       | Store accumulator into memory |
| 30   | ADD         | Add memory value to accumulator |
| 31   | SUBTRACT    | Subtract memory value from accumulator |
| 32   | DIVIDE      | Divide accumulator by memory value |
| 33   | MULTIPLY    | Multiply accumulator by memory value |
| 40   | BRANCH      | Jump to a memory location |
| 41   | BRANCHNEG   | Jump if accumulator is negative |
| 42   | BRANCHZERO  | Jump if accumulator is zero |
| 43   | HALT        | Stop the program |

➡️ **Instruction format:**  

Old Format (4 digit words):
- First 2 digits → Operation code  
- Last 2 digits → Memory address operand

New Format (6 digit words):
- First 3 digits → Operation code
- Last 3 digits → Memory address operand

**Example:**  
`2007` → LOAD (20) from memory location (07)
`020007` → LOAD (20) from memory location (07)

---

## 👤 Authors
Developed by **Darby Thomas**, **Ethan Rasmussen**, and **Kyle Greer**

---

✅ **New Features:**  
- File saving via **File → Save**  
- Support for 6 digit words
- Memory editing by **double-clicking** on memory cells
- **Clear** memory entries interactively
- System-wide **custom color themes**
- Open multiple instances via **File → Open New Window**