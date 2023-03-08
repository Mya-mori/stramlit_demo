```bash
conda create --name streamlit-task -c https://repo.anaconda.com/pkgs/snowflake python=3.8

conda activate streamlit-task

conda install -c https://repo.anaconda.com/pkgs/snowflake snowflake-snowpark-python pandas notebook scikit-learn cachetools

pip install streamlit

pip install plotly

pip install streamlit-aggrid

streamlit run taskmanager.py
```