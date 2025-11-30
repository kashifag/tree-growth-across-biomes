#Tree Growth Across Biomes
### *A Dynamic Visualization of Hierarchical Models — Built with Streamlit + Python*

**Inspiration**


Adapted from 
Matthew Kay’s “Hierarchical Models Explained”
Re-imagined in Python for ecological and bioinformatics education.

**Author**

**Kashifa Ghazal**
MSc Bioinformatics, University of Bristol

![cover](https://user-images.githubusercontent.com/00000000/forest-cover.gif)

> *"Not all trees grow alike — but they still follow the same laws of nature."*  
> This interactive app explores how tree height relates to trunk diameter across five biomes,  
> and how different statistical pooling strategies can change our understanding of growth.

---

## Live Demo
**[Launch the App](https://tree-growth-across-biomes-6nyeznpyxfdtufuldygvn3.streamlit.app)** (hosted on Streamlit Cloud)  
*(If you’re running locally, see instructions below.)*

---

## What This Project Shows
This project brings the idea of **hierarchical (mixed-effects) models** to life.  
It compares three modeling philosophies:

| Mode | Description | Model |
|------|--------------|----------|
| **No Pooling** | Each biome builds its *own* regression — great freedom, high variance. | `OLS per biome` |
| **Complete Pooling** | Treats all trees as one forest — ignores biome identity. | `Global OLS` |
| **Partial Pooling** | Biomes share information through random effects — the best of both worlds. | `MixedLM (random intercepts & slopes)` |

The “shrinkage” you see in the partial-pooling view shows how small, noisy groups borrow strength from the global trend — a cornerstone idea in modern biostatistics, ecology, and genomics.

---

## Tech Stack
| Tool | Purpose |
|------|----------|
| **Python** | Core language |
| **Streamlit** | Interactive web app |
| **Plotly** | Dynamic, colorful visualization |
| **Statsmodels** | Linear & mixed-effects models |
| **Pandas + NumPy** | Data simulation & manipulation |

---

## Why It Matters (Bioinformatics Angle)
Hierarchical thinking appears everywhere in biology:
- **Gene expression:** cells nested within individuals  
- **Clinical trials:** patients nested within sites  
- **Ecology:** trees nested within biomes  

Partial pooling lets us capture **both shared biology and local variation** — exactly the balance real data demands.

---

## Run Locally
```bash
git clone https://github.com/kashifag/tree-growth-across-biomes.git
cd tree-growth-across-biomes
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app_streamlit.py

tree-growth-across-biomes/
├── app_streamlit.py        # main Streamlit app
├── requirements.txt        # dependencies
├── data/trees_biomes.csv   # simulated dataset
└── README.md               # you are here

Quick Summary
This project visualizes how data-sharing between groups (partial pooling) stabilizes models in biology and ecology; a fun, hands-on example of statistics meeting nature.


