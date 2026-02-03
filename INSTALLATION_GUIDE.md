# Installation Guide for Claude Code

## 📦 Installing the Aviation Engineer Agent Skill in Claude Code

Follow these steps to install your skill in Claude Code desktop application.

---

## Step 1: Locate Claude Code Skills Directory

**On Windows:**
```
C:\Users\[YourUsername]\.claude\skills\
```

**On macOS:**
```
/Users/[YourUsername]/.claude/skills/
```

**On Linux:**
```
/home/[YourUsername]/.claude/skills/
```

**How to find it in Claude Code:**
1. Open Claude Code
2. Open a terminal (View → Terminal or Ctrl+`)
3. Type: `echo $HOME/.claude/skills` (Mac/Linux) or `echo %USERPROFILE%\.claude\skills` (Windows)

---

## Step 2: Create the Skill Directory

In your terminal (within Claude Code or system terminal):

**Mac/Linux:**
```bash
mkdir -p ~/.claude/skills/aviation-engineer-agent
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\.claude\skills\aviation-engineer-agent" -Force
```

---

## Step 3: Copy Skill Files

Copy all files from this package into the newly created directory:

**Files to copy:**
- `SKILL.md` → Main skill instructions (REQUIRED)
- `README.md` → Documentation
- `QUICKREF.md` → Quick reference
- `Fleet_Database_SkyTech.xlsx` → Sample fleet data

**Copy command (Mac/Linux):**
```bash
# Navigate to where you downloaded this package, then:
cp -r * ~/.claude/skills/aviation-engineer-agent/
```

**Copy command (Windows):**
```powershell
# Navigate to download location, then:
Copy-Item -Path * -Destination "$env:USERPROFILE\.claude\skills\aviation-engineer-agent\" -Recurse
```

**Or use GUI:**
Simply drag and drop all files into the `aviation-engineer-agent` folder.

---

## Step 4: Verify Installation

**In Claude Code terminal:**
```bash
# Mac/Linux
ls ~/.claude/skills/aviation-engineer-agent/

# Windows
dir %USERPROFILE%\.claude\skills\aviation-engineer-agent\
```

**You should see:**
```
SKILL.md
README.md
QUICKREF.md
Fleet_Database_SkyTech.xlsx
INSTALLATION_GUIDE.md
```

---

## Step 5: Restart Claude Code (if needed)

Some versions of Claude Code auto-detect new skills, others require restart:
1. Close Claude Code completely
2. Reopen Claude Code
3. Your skill should now appear in the skills list

---

## Step 6: Test the Skill

### Quick Test:
1. Download a sample AD PDF (or use the test below)
2. In Claude Code, upload the AD PDF
3. Upload `Fleet_Database_SkyTech.xlsx`
4. Say: **"Evaluate this AD against my fleet using the aviation-engineer-agent skill"**

### Create a Test AD (if you don't have a real one):

Create a file named `TEST_AD.txt`:
```
AIRWORTHINESS DIRECTIVE 2026-01-TEST
Pilatus Aircraft Ltd.

Docket No. FAA-2026-TEST
Effective Date: February 1, 2026

APPLICABILITY:
This AD applies to Pilatus Aircraft Ltd. Model PC-12/47 airplanes,
manufacturer serial numbers (MSN) 1200 through 1300, certificated in any category.

SUBJECT: Test Landing Gear Inspection

COMPLIANCE:
Required within 100 hours time-in-service after the effective date of this AD.

REQUIRED ACTIONS:
(a) Inspect the nose landing gear drag link for cracks.
(b) If cracks are found, replace the component before further flight.
(c) Repeat inspection every 100 hours time-in-service.

REFERENCE:
Service Bulletin No. 32-TEST, dated January 15, 2026.
```

Upload this test file and the fleet database to Claude Code, then ask for evaluation.

---

## Troubleshooting

### Issue: "Skill not showing in Claude Code"

**Solution 1:** Check file location
```bash
# Mac/Linux - verify SKILL.md exists
cat ~/.claude/skills/aviation-engineer-agent/SKILL.md | head -5

# Windows
type %USERPROFILE%\.claude\skills\aviation-engineer-agent\SKILL.md
```

**Solution 2:** Check permissions
```bash
# Mac/Linux - ensure files are readable
chmod -R 755 ~/.claude/skills/aviation-engineer-agent/
```

**Solution 3:** Restart Claude Code completely

**Solution 4:** Check Claude Code version
- Skills feature might require Claude Code v1.x or newer
- Update Claude Code if needed

### Issue: "Cannot read SKILL.md"

**Solution:** Verify file encoding is UTF-8
- Open SKILL.md in a text editor
- Save as UTF-8 (no BOM)

### Issue: "Skill runs but Python libraries missing"

**Solution:** Install required packages in Claude Code terminal
```bash
pip install pandas openpyxl pdfplumber pypdf2
```

---

## How to Use After Installation

**Basic Usage:**
```
1. Upload AD/SB PDF to Claude Code
2. Upload your fleet Excel database
3. Say: "Evaluate this AD using aviation-engineer-agent skill"
```

**Alternative phrasing:**
- "Use the aviation engineer skill to check this AD"
- "Check AD applicability with the aviation-engineer-agent skill"
- "Evaluate AD against fleet database"

Claude Code will automatically:
1. Read the SKILL.md file
2. Follow the instructions there
3. Process your AD and fleet data
4. Generate evaluation report

---

## Updating the Skill

To modify skill behavior:
1. Open `~/.claude/skills/aviation-engineer-agent/SKILL.md`
2. Edit the workflow sections
3. Save the file
4. Changes apply immediately (no restart needed)

---

## Getting Help

**If skill doesn't work:**
1. Check Claude Code terminal for error messages
2. Verify all files copied correctly
3. Ensure fleet database has required columns
4. Try the test AD first (simpler than real ADs)

**For skill improvements:**
- Edit SKILL.md directly
- Test changes with sample AD
- Iterate based on results

---

## File Structure Reference

```
~/.claude/skills/aviation-engineer-agent/
│
├── SKILL.md              ← Claude Code reads this (REQUIRED)
├── README.md             ← Documentation for users
├── QUICKREF.md           ← Quick reference
├── Fleet_Database_SkyTech.xlsx  ← Sample data
└── INSTALLATION_GUIDE.md ← This file
```

---

## Success Indicators

✅ Skill directory exists at `~/.claude/skills/aviation-engineer-agent/`  
✅ SKILL.md file is present and readable  
✅ Claude Code shows the skill in skills list (if it has a UI for this)  
✅ Can reference skill by name in Claude Code chat  
✅ Test AD evaluation completes successfully  

---

**You're all set!** The skill is now ready to use in Claude Code.

For questions about skill behavior, see README.md  
For quick commands, see QUICKREF.md
