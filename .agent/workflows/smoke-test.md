# /smoke-test Workflow

1. Start the Flask application server in background mode or on a designated test port:
   `flask run --port=5000`
2. Launch browser subagent or automated client.
3. Complete one full user flow for each module:
   - Module 1 (Disease): Upload a sample leaf image, verify top-3 predictions, confidence score, Grad-CAM heatmap, and advisory disclaimer. Test uncertain/non-leaf image behavior.
   - Module 2 (Yield): Submit form values (crop, rainfall, temp, humidity, pH, N, P, K, area) and inspect predicted yield and feature importances.
   - Module 3 (Recommend): Submit soil/weather parameters and inspect top-3 crop recommendations.
   - Module 4 (Price): Select a crop, inspect historical chart, 7-day forecast line, and baseline comparison.
   - Module 5 (Advisor): Complete cross-module advisor wizard and verify yield, price, revenue calculation, and disease risk disclaimer.
   - User History & Language: Toggle English/Hindi language switch; inspect history table.
4. Verify mobile responsiveness at 360px viewport.
5. Capture screenshots for each page and save them to `docs/screenshots/`.
6. Terminate the test server.
