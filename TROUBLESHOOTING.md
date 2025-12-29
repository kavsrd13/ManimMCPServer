# 🎬 Animation Generator - Quick Troubleshooting Guide

## ✅ Your Setup is Working!

All systems tested successfully:
- ✓ Azure OpenAI API (gpt-4.1)
- ✓ Animation Server (Azure Container Apps)
- ✓ Local Python environment
- ✓ Streamlit app

---

## 🚀 How to Use

### Start the App
```powershell
streamlit run streamlit_app.py
```

Then open: **http://localhost:8501**

### Try These Test Prompts

1. **Simple (Always works)**:
   ```
   Create a blue circle
   ```

2. **Transform**:
   ```
   Blue circle morphing into a red square
   ```

3. **Math**:
   ```
   Show a² + b² = c²
   ```

4. **Complex**:
   ```
   Explain gradient descent with a ball rolling down a curve
   ```

---

## 🔧 If You See "Animation generation failed"

### Step 1: Check Error Details
The improved app now shows:
- Full error message
- Server URL being used
- HTTP status code
- Generated code that failed
- Enhanced prompt used

### Step 2: Common Issues & Fixes

#### Issue: "Manim execution failed"
**Cause**: Generated code has syntax errors or uses forbidden features

**Solutions**:
- Try a simpler prompt
- Avoid complex math (LaTeX not available)
- Check the "Generated Code" section for errors
- Look for MathTex or Tex usage (not allowed)

#### Issue: "Request timed out"
**Cause**: Animation too complex (>5 minutes to render)

**Solutions**:
- Simplify your prompt
- Reduce animation duration
- Use fewer objects/transformations

#### Issue: "Cannot connect to animation server"
**Cause**: Network/internet issue or server down

**Solutions**:
- Check internet connection
- Verify server status: https://manim-mcp-app.salmonforest-f54e4566.eastus.azurecontainerapps.io/status
- Should return: `{"status": "healthy"}`

---

## 🧪 Test Your Setup Anytime

Run the diagnostic script:
```powershell
python test_full_pipeline.py
```

This tests:
1. Azure OpenAI credentials
2. API connection
3. Prompt enhancement
4. Code generation
5. Server connection
6. Animation rendering

---

## 📝 What Changed (Improvements)

### Better Error Handling
- Shows server URL being used
- HTTP status codes displayed
- More detailed error messages
- Timeout handled separately
- Connection errors explained

### More Debugging Info
- Enhanced prompt shown in errors
- Generated code always visible
- Server information included
- Helpful tips for each error type

---

## 🎯 Animation Best Practices

### DO:
✓ Use simple shapes (Circle, Square, Rectangle)
✓ Use Text() for all text and math
✓ Use Unicode for math symbols: ², ³, √, π, ∑
✓ Keep animations under 15 seconds
✓ Be specific about colors and positions
✓ Test with simple prompts first

### DON'T:
✗ Use MathTex() or Tex() (LaTeX not available)
✗ Make overly complex animations
✗ Use vague descriptions
✗ Request very long animations (>30 seconds)

---

## 📊 Server Status

**Production Server**: 
https://manim-mcp-app.salmonforest-f54e4566.eastus.azurecontainerapps.io

**Check if online**:
```powershell
curl https://manim-mcp-app.salmonforest-f54e4566.eastus.azurecontainerapps.io/status
```

Should return: `{"status":"healthy"}`

---

## 🆘 Still Having Issues?

1. **Run the diagnostic**: `python test_full_pipeline.py`
2. **Check error details** in the expanded sections
3. **Try the simple test**: "Create a blue circle"
4. **Look at generated code** for syntax errors
5. **Verify server is online** (check status endpoint)

---

## ✨ Success Checklist

Before trying complex animations:
- [ ] Simple test works ("Create a blue circle")
- [ ] Credentials are loaded (check sidebar)
- [ ] Server status is healthy
- [ ] Diagnostic test passes

Once these work, you can try more complex animations!

---

**Created**: December 29, 2025
**Status**: All systems operational ✅
