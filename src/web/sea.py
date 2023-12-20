import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Sample data for market segmentation (replace with your actual data)
data = pd.DataFrame({
    'CustomerID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'Age': [25, 30, 35, 40, 45, 50, 55, 60, 65, 70],
    'Income': [50000, 60000, 70000, 80000, 90000, 100000, 110000, 120000, 130000, 140000],
    'Segment': ['A', 'B', 'C', 'B', 'A', 'C', 'B', 'A', 'C', 'B']
})

# Sidebar
st.sidebar.title("Market Segmentation")

# Data display options
st.sidebar.checkbox("Show Data", True)

# Segmentation options
segmentation_methods = ["Shade", "ID3"]
selected_method = st.sidebar.selectbox("Select Segmentation Method", segmentation_methods)

# Filtering data based on segmentation method
if selected_method == "Shade":
    segmented_data = data[data['Segment'] == 'A']
else:
    segmented_data = data[data['Segment'] == 'B']

# Page title and description
st.title("Market Segmentation Results")
st.markdown("Visualize market segments, their characteristics, and behavior patterns.")

# Show the segmented data
if st.sidebar.checkbox("Show Segmented Data"):
    st.subheader("Segmented Customer Data:")
    st.write(segmented_data)

# Visualize market segments
st.subheader("Segment Distribution:")
plt.figure(figsize=(8, 6))
sns.countplot(data=segmented_data, x='Segment')
plt.xlabel("Segment")
plt.ylabel("Count")
st.pyplot()

# Characteristics and behavior patterns
st.subheader("Segment Characteristics and Behavior Patterns:")
# You can add more analysis and visualizations here based on your data

# Detailed insights and recommendations
st.subheader("Detailed Insights and Recommendations:")
st.markdown("Provide detailed insights and recommendations for each segment.")

# You can provide recommendations and insights based on the selected segment.

# Example recommendation for Segment A
if selected_method == "Shade":
    if 'A' in segmented_data['Segment'].values:
        st.write("Recommendation for Segment A:")
        st.markdown("- Target younger customers (age < 40).")
        st.markdown("- Focus on customers with lower income (< $70,000).")
else:
    if 'B' in segmented_data['Segment'].values:
        st.write("Recommendation for Segment B:")
        st.markdown("- Target middle-aged customers (age 40-60).")
        st.markdown("- Focus on customers with moderate income ($70,000 - $100,000).")

# Additional recommendations and insights can be added based on your analysis.

# You can include more visualizations and insights as needed.

# For more interactivity, you can allow users to select a specific segment and display insights for that segment.

# Run the app using: streamlit run app.py
