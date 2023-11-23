from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def get_chart_page():
    # Create a Matplotlib chart and save it to BytesIO
    plt.figure(figsize=(8, 5))
    plt.bar(["Level", "Relevance"], [4, 3], color="royalblue")
    plt.title("Maslow's Hierarchy Positioning Comparison")
    chart_bytes = BytesIO()
    plt.savefig(chart_bytes, format="png", bbox_inches="tight", dpi=300)
    chart_bytes.seek(0)

    # Encode the chart bytes to base64
    chart_base64 = base64.b64encode(chart_bytes.read()).decode()

    # Generate an HTML page with the chart embedded
    html_content = f"""
    <html>
        <head>
            <title>Chart Page</title>
        </head>
        <body>
            <h1>Chart Page</h1>
            <img src="data:image/png;base64,{chart_base64}" alt="Chart">
        </body>
    </html>
    """
    chart_bytes.close()
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI app using Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
