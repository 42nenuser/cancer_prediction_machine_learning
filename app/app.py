import streamlit as st
import pickle
import pandas as pd
import plotly.graph_objects as go
import numpy as np


def get_clean_data():
    """Loads and cleans the dataset."""
    data = pd.read_csv("data.csv")
    
    # Drop unnecessary columns
    data = data.drop(['Unnamed: 32', 'id'], axis=1)
    
    # Encode diagnosis (M = 1, B = 0)
    data['diagnosis'] = data['diagnosis'].map({'M': 1, 'B': 0})
    
    return data


def add_sidebar():
    """Creates the sidebar with sliders for feature selection."""
    st.sidebar.header("🔬 Cell Nuclei Measurements")
    
    data = get_clean_data()
    
    slider_labels = [
        ("Radius (mean)", "radius_mean"),
        ("Texture (mean)", "texture_mean"),
        ("Perimeter (mean)", "perimeter_mean"),
        ("Area (mean)", "area_mean"),
        ("Smoothness (mean)", "smoothness_mean"),
        ("Compactness (mean)", "compactness_mean"),
        ("Concavity (mean)", "concavity_mean"),
        ("Concave points (mean)", "concave points_mean"),
        ("Symmetry (mean)", "symmetry_mean"),
        ("Fractal dimension (mean)", "fractal_dimension_mean"),
        ("Radius (se)", "radius_se"),
        ("Texture (se)", "texture_se"),
        ("Perimeter (se)", "perimeter_se"),
        ("Area (se)", "area_se"),
        ("Smoothness (se)", "smoothness_se"),
        ("Compactness (se)", "compactness_se"),
        ("Concavity (se)", "concavity_se"),
        ("Concave points (se)", "concave points_se"),
        ("Symmetry (se)", "symmetry_se"),
        ("Fractal dimension (se)", "fractal_dimension_se"),
        ("Radius (worst)", "radius_worst"),
        ("Texture (worst)", "texture_worst"),
        ("Perimeter (worst)", "perimeter_worst"),
        ("Area (worst)", "area_worst"),
        ("Smoothness (worst)", "smoothness_worst"),
        ("Compactness (worst)", "compactness_worst"),
        ("Concavity (worst)", "concavity_worst"),
        ("Concave points (worst)", "concave points_worst"),
        ("Symmetry (worst)", "symmetry_worst"),
        ("Fractal dimension (worst)", "fractal_dimension_worst"),
    ]

    input_dict = {}

    for label, key in slider_labels:
        input_dict[key] = st.sidebar.slider(
            label,
            min_value=float(0),
            max_value=float(data[key].max()),
            value=float(data[key].mean())
        )
    
    return input_dict


def get_radar_chart(input_data):
    """Normalizes the input data for radar chart visualization."""
    data = get_clean_data()
    
    X = data.drop(['diagnosis'], axis=1)
    
    scaled_dict = {}
    
    for key, value in input_data.items():
        max_val = X[key].max()
        min_val = X[key].min()
        scaled_value = (value - min_val) / (max_val - min_val) if max_val != min_val else 0
        scaled_dict[key] = scaled_value
    
    return scaled_dict


def get_improved_radar_chart(input_data):
    """Generates a radar chart with better readability and UI improvements."""
    categories = [
        'Radius', 'Texture', 'Perimeter', 'Area', 
        'Smoothness', 'Compactness', 
        'Concavity', 'Concave Points',
        'Symmetry', 'Fractal Dimension'
    ]

    # Correct column mapping to match dataset keys
    column_mapping = {
        "Radius": "radius",
        "Texture": "texture",
        "Perimeter": "perimeter",
        "Area": "area",
        "Smoothness": "smoothness",
        "Compactness": "compactness",
        "Concavity": "concavity",
        "Concave Points": "concave points",
        "Symmetry": "symmetry",
        "Fractal Dimension": "fractal_dimension"  # Fixes the issue
    }

    # Extracting and normalizing values
    values_mean = [input_data[f"{column_mapping[c]}_mean"] for c in categories]
    values_se = [input_data[f"{column_mapping[c]}_se"] for c in categories]
    values_worst = [input_data[f"{column_mapping[c]}_worst"] for c in categories]

    # Normalize values to range [0, 1]
    max_value = max(values_mean + values_se + values_worst)
    values_mean = [v / max_value for v in values_mean]
    values_se = [v / max_value for v in values_se]
    values_worst = [v / max_value for v in values_worst]

    fig = go.Figure()

    # Mean values
    fig.add_trace(go.Scatterpolar(
        r=values_mean,
        theta=categories,
        fill='toself',
        name='Mean Value',
        marker=dict(color='blue'),
        opacity=0.6
    ))

    # Standard Error values
    fig.add_trace(go.Scatterpolar(
        r=values_se,
        theta=categories,
        fill='toself',
        name='Standard Error',
        marker=dict(color='gray'),
        line=dict(dash='dot'),
        opacity=0.8
    ))

    # Worst-case values
    fig.add_trace(go.Scatterpolar(
        r=values_worst,
        theta=categories,
        fill='toself',
        name='Worst Value',
        marker=dict(color='red'),
        opacity=0.5
    ))

    fig.update_layout(
        title="📊 Breast Cancer Feature Analysis",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],  
                showticklabels=True,  
                tickmode="array",
                tickvals=np.linspace(0, 1, 5),
                ticktext=["0%", "25%", "50%", "75%", "100%"],
                gridcolor="gray",
                gridwidth=0.3
            )
        ),
        legend=dict(
            title="Feature Categories",
            orientation="h",
            yanchor="bottom",
            y=-0.2
        ),
        showlegend=True
    )

    return fig



def add_predictions(input_data):
    """Loads the trained model and makes predictions."""
    model = pickle.load(open("model.pkl", "rb"))
    scaler = pickle.load(open("scaler.pkl", "rb"))
    
    input_array = np.array(list(input_data.values())).reshape(1, -1)
    input_array_scaled = scaler.transform(input_array)
    
    prediction = model.predict(input_array_scaled)
    
    st.subheader("🩺 Cell Cluster Prediction")
    st.write("The cell cluster is:")

    if prediction[0] == 0:
        st.write("<span class='diagnosis benign'>Benign</span>", unsafe_allow_html=True)
    else:
        st.write("<span class='diagnosis malicious'>Malignant</span>", unsafe_allow_html=True)
    
    st.write("🔹 Probability of being benign: ", round(model.predict_proba(input_array_scaled)[0][0], 4))
    st.write("🔹 Probability of being malignant: ", round(model.predict_proba(input_array_scaled)[0][1], 4))
    st.write("⚠️ This app assists in diagnosis but does NOT replace professional medical advice.")


def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(
        page_title="Breast Cancer Predictor",
        page_icon=":female-doctor:",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    with open("style.css") as f:
        st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

    input_data = add_sidebar()

    st.title("🎗️ Breast Cancer Predictor")
    st.write("📌 Use this tool to analyze breast cancer cell measurements.")

    col1, col2 = st.columns([4, 1])

    with col1:
        radar_chart = get_improved_radar_chart(get_radar_chart(input_data))
        st.plotly_chart(radar_chart)
    with col2:
        add_predictions(input_data)


if __name__ == '__main__':
    main()
