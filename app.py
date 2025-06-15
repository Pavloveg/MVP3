import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Настройка страницы
st.set_page_config(
    page_title="Анализ зарплат в России",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомные стили
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Заголовок приложения
st.markdown('<h1 class="main-header">📊 Анализ динамики зарплат в России (2000-2024)</h1>', unsafe_allow_html=True)

# Загрузка данных
@st.cache_data
def load_data():
    """Загружает данные для анализа"""
    try:
        data = pd.read_csv('data/salary_analysis_data.csv')
        return data
    except FileNotFoundError:
        st.error("Файл с данными не найден. Убедитесь, что файл salary_analysis_data.csv находится в папке data/")
        return None

# Функция для расчета метрик
def calculate_metrics(data, sector, start_year=2000, end_year=2024):
    """Рассчитывает ключевые метрики для отрасли"""
    sector_data = data[data['Отрасль'] == sector]
    
    start_data = sector_data[sector_data['Год'] == start_year]
    end_data = sector_data[sector_data['Год'] == end_year]
    
    if len(start_data) == 0 or len(end_data) == 0:
        return None
        
    start_salary = start_data['Зарплата'].iloc[0]
    end_salary = end_data['Зарплата'].iloc[0]
    start_real_salary = start_data['Реальная_зарплата'].iloc[0]
    end_real_salary = end_data['Реальная_зарплата'].iloc[0]
    
    nominal_growth = end_salary / start_salary
    real_growth = end_real_salary / start_real_salary
    years_diff = end_year - start_year
    avg_nominal_growth = (nominal_growth ** (1/years_diff) - 1) * 100
    avg_real_growth = (real_growth ** (1/years_diff) - 1) * 100
    
    return {
        'start_salary': start_salary,
        'end_salary': end_salary,
        'start_real_salary': start_real_salary,
        'end_real_salary': end_real_salary,
        'nominal_growth': nominal_growth,
        'real_growth': real_growth,
        'avg_nominal_growth': avg_nominal_growth,
        'avg_real_growth': avg_real_growth
    }

# Загружаем данные
data = load_data()

if data is not None:
    # Боковая панель с фильтрами
    st.sidebar.header("🎛️ Настройки анализа")
    
    # Выбор отраслей
    available_sectors = data['Отрасль'].unique().tolist()
    selected_sectors = st.sidebar.multiselect(
        "Выберите отрасли для анализа:",
        available_sectors,
        default=available_sectors
    )
    
    # Выбор временного периода
    min_year = int(data['Год'].min())
    max_year = int(data['Год'].max())
    
    year_range = st.sidebar.slider(
        "Выберите период анализа:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1
    )
    
    # Фильтрация данных
    filtered_data = data[
        (data['Отрасль'].isin(selected_sectors)) &
        (data['Год'] >= year_range[0]) &
        (data['Год'] <= year_range[1])
    ]
    
    if len(filtered_data) > 0:
        # Основные метрики
        st.header("📈 Ключевые показатели")
        
        cols = st.columns(len(selected_sectors))
        
        for i, sector in enumerate(selected_sectors):
            with cols[i]:
                metrics = calculate_metrics(data, sector, year_range[0], year_range[1])
                if metrics:
                    st.markdown(f"**{sector}**")
                    st.metric(
                        f"Зарплата {year_range[1]}",
                        f"{metrics['end_salary']:,.0f} ₽",
                        f"+{(metrics['nominal_growth']-1)*100:.0f}% за период"
                    )
                    st.metric(
                        "Реальный рост",
                        f"{metrics['real_growth']:.1f}x",
                        f"{metrics['avg_real_growth']:.1f}% в год"
                    )
        
        # Графики
        st.header("📊 Визуализация данных")
        
        # Выбор типа графика
        chart_type = st.selectbox(
            "Выберите тип данных для отображения:",
            ["Номинальные зарплаты", "Реальные зарплаты", "Сравнение роста", "Инфляция"]
        )
        
        if chart_type == "Номинальные зарплаты":
            fig = px.line(
                filtered_data,
                x='Год',
                y='Зарплата',
                color='Отрасль',
                title='Динамика номинальных зарплат',
                labels={'Зарплата': 'Зарплата, руб'},
                height=600
            )
            fig.update_traces(mode='lines+markers', line=dict(width=3), marker=dict(size=6))
            fig.update_layout(
                title_font_size=18,
                xaxis_title_font_size=14,
                yaxis_title_font_size=14,
                legend_font_size=12
            )
            st.plotly_chart(fig, use_container_width=True)
            
        elif chart_type == "Реальные зарплаты":
            fig = px.line(
                filtered_data,
                x='Год',
                y='Реальная_зарплата',
                color='Отрасль',
                title='Динамика реальных зарплат (в ценах 2000 года)',
                labels={'Реальная_зарплата': 'Реальная зарплата, руб'},
                height=600
            )
            fig.update_traces(mode='lines+markers', line=dict(width=3), marker=dict(size=6))
            fig.update_layout(
                title_font_size=18,
                xaxis_title_font_size=14,
                yaxis_title_font_size=14,
                legend_font_size=12
            )
            st.plotly_chart(fig, use_container_width=True)
            
        elif chart_type == "Сравнение роста":
            # Создаем данные для сравнения роста
            growth_data = []
            for sector in selected_sectors:
                metrics = calculate_metrics(data, sector, year_range[0], year_range[1])
                if metrics:
                    growth_data.append({
                        'Отрасль': sector,
                        'Номинальный рост': metrics['nominal_growth'],
                        'Реальный рост': metrics['real_growth']
                    })
            
            if growth_data:
                growth_df = pd.DataFrame(growth_data)
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name='Номинальный рост',
                    x=growth_df['Отрасль'],
                    y=growth_df['Номинальный рост'],
                    marker_color='steelblue',
                    opacity=0.8
                ))
                
                fig.add_trace(go.Bar(
                    name='Реальный рост',
                    x=growth_df['Отрасль'],
                    y=growth_df['Реальный рост'],
                    marker_color='darkorange',
                    opacity=0.8
                ))
                
                fig.update_layout(
                    title=f'Сравнение номинального и реального роста ({year_range[0]}-{year_range[1]})',
                    xaxis_title='Отрасль',
                    yaxis_title='Рост, раз',
                    barmode='group',
                    height=600,
                    title_font_size=18,
                    xaxis_title_font_size=14,
                    yaxis_title_font_size=14,
                    legend_font_size=12
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
        elif chart_type == "Инфляция":
            # График инфляции
            inflation_data = filtered_data.drop_duplicates(subset=['Год'])[['Год', 'Инфляция', 'Кумулятивная_инфляция']].sort_values('Год')
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Годовая инфляция', 'Кумулятивная инфляция'),
                vertical_spacing=0.12
            )
            
            # Годовая инфляция
            colors = ['darkred' if inf > 10 else 'red' for inf in inflation_data['Инфляция']]
            
            fig.add_trace(
                go.Bar(
                    x=inflation_data['Год'],
                    y=inflation_data['Инфляция'],
                    marker_color=colors,
                    name='Инфляция',
                    opacity=0.7
                ),
                row=1, col=1
            )
            
            fig.add_hline(y=10, line_dash="dash", line_color="black", 
                         annotation_text="Высокая инфляция (>10%)", row=1, col=1)
            
            # Кумулятивная инфляция
            fig.add_trace(
                go.Scatter(
                    x=inflation_data['Год'],
                    y=inflation_data['Кумулятивная_инфляция'],
                    mode='lines+markers',
                    line=dict(color='darkred', width=3),
                    marker=dict(size=6),
                    name='Кумулятивная инфляция'
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                title_text='Анализ инфляции в России',
                height=800,
                title_font_size=18,
                showlegend=False
            )
            
            fig.update_xaxes(title_text="Год", title_font_size=14, row=1, col=1)
            fig.update_xaxes(title_text="Год", title_font_size=14, row=2, col=1)
            fig.update_yaxes(title_text="Инфляция, %", title_font_size=14, row=1, col=1)
            fig.update_yaxes(title_text="Кумулятивный коэффициент", title_font_size=14, row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Таблица с данными
        st.header("📋 Детальные данные")
        
        if st.checkbox("Показать подробную таблицу"):
            # Форматируем данные для отображения
            display_data = filtered_data.copy()
            display_data['Зарплата'] = display_data['Зарплата'].round(0).astype(int)
            display_data['Реальная_зарплата'] = display_data['Реальная_зарплата'].round(0).astype(int)
            display_data['Инфляция'] = display_data['Инфляция'].round(1)
            display_data['Кумулятивная_инфляция'] = display_data['Кумулятивная_инфляция'].round(2)
            
            st.dataframe(
                display_data,
                use_container_width=True,
                height=400
            )
        
        # Выводы и аналитика
        st.header("🎯 Аналитические выводы")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Номинальный рост")
            for sector in selected_sectors:
                metrics = calculate_metrics(data, sector, year_range[0], year_range[1])
                if metrics:
                    st.write(f"**{sector}**: {metrics['nominal_growth']:.1f}x ({metrics['avg_nominal_growth']:.1f}% в год)")
        
        with col2:
            st.subheader("Реальный рост")
            for sector in selected_sectors:
                metrics = calculate_metrics(data, sector, year_range[0], year_range[1])
                if metrics:
                    st.write(f"**{sector}**: {metrics['real_growth']:.1f}x ({metrics['avg_real_growth']:.1f}% в год)")
        
        # Общие выводы
        st.subheader("Общие выводы")
        
        if len(filtered_data) > 0:
            avg_inflation = filtered_data.drop_duplicates(subset=['Год'])['Инфляция'].mean()
            max_inflation_year = filtered_data.drop_duplicates(subset=['Год']).loc[filtered_data.drop_duplicates(subset=['Год'])['Инфляция'].idxmax(), 'Год']
            max_inflation_value = filtered_data.drop_duplicates(subset=['Год'])['Инфляция'].max()
            
            st.write(f"• Средний уровень инфляции за выбранный период: **{avg_inflation:.1f}%**")
            st.write(f"• Максимальная инфляция: **{max_inflation_value:.1f}%** в {max_inflation_year} году")
            st.write(f"• Анализируется период: **{year_range[0]}-{year_range[1]}** ({year_range[1] - year_range[0]} лет)")
            
            if len(selected_sectors) > 1:
                # Находим лидера по реальному росту
                best_real_growth = 0
                best_sector = ""
                for sector in selected_sectors:
                    metrics = calculate_metrics(data, sector, year_range[0], year_range[1])
                    if metrics and metrics['real_growth'] > best_real_growth:
                        best_real_growth = metrics['real_growth']
                        best_sector = sector
                
                if best_sector:
                    st.write(f"• Лидер по реальному росту зарплат: **{best_sector}** ({best_real_growth:.1f}x)")
    
    else:
        st.warning("Для выбранных параметров данные не найдены. Попробуйте изменить фильтры.")

# Информация о проекте
st.sidebar.markdown("---")
st.sidebar.header("ℹ️ О проекте")
st.sidebar.markdown("""
**Источники данных:**
- Росстат (зарплаты)
- ЦБ РФ (инфляция)

**Период анализа:** 2000-2024

**Методология:** Реальные зарплаты рассчитаны в ценах 2000 года с учетом кумулятивной инфляции.
""")

st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Совет:** Используйте фильтры выше для детального анализа интересующих вас отраслей и периодов.")