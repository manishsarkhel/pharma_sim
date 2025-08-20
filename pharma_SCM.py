import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

# Set page config
st.set_page_config(page_title="Pharma Supply Chain Sim", layout="wide", page_icon="💊")

# Title and introduction
st.title("💊 Pharmaceutical Supply Chain Simulation 🚚")
st.markdown("""
This simulation demonstrates how decisions at one point in the pharmaceutical supply chain 
affect the entire system. Work in small groups to manage different aspects of the supply chain
and make decisions under varying conditions.
""")

# Initialize session state variables
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.week = 1
    st.session_state.money = 1000000
    st.session_state.inventory = {
        'raw_materials': 5000,
        'api': 3000,
        'finished_products': 2000
    }
    st.session_state.demand = 500
    st.session_state.events = []
    st.session_state.kpis = {
        'inventory_turnover': [],
        'otif': [],
        'costs': [],
        'revenue': []
    }
    st.session_state.history = []

# Sidebar for simulation controls
with st.sidebar:
    st.header("⚙️ Simulation Controls")
    
    if st.button("Next Week ➡️"):
        # Record previous state
        st.session_state.history.append({
            'week': st.session_state.week,
            'money': st.session_state.money,
            'inventory': st.session_state.inventory.copy(),
            'demand': st.session_state.demand
        })
        
        # Progress time
        st.session_state.week += 1
        
        # Random events
        if random.random() < 0.3:  # 30% chance of an event
            possible_events = [
                {"name": "📜 Regulatory Change", "effect": "Production slowed by 20%"},
                {"name": "📈 Demand Spike", "effect": "Demand increased by 30%"},
                {"name": "📉 Raw Material Shortage", "effect": "Raw material costs increased by 25%"},
                {"name": "🔬 Quality Issue", "effect": "10% of production batch rejected"},
                {"name": "❄️ Cold Chain Failure", "effect": "5% of finished products lost"}
            ]
            event = random.choice(possible_events)
            st.session_state.events.append(f"Week {st.session_state.week}: {event['name']} - {event['effect']}")
            
            # Apply event effects
            if "Demand Spike" in event['name']:
                st.session_state.demand = int(st.session_state.demand * 1.3)
            elif "Raw Material Shortage" in event['name']:
                st.session_state.money -= int(st.session_state.inventory['raw_materials'] * 0.25)
            elif "Quality Issue" in event['name']:
                st.session_state.inventory['finished_products'] = int(st.session_state.inventory['finished_products'] * 0.9)
            elif "Cold Chain Failure" in event['name']:
                st.session_state.inventory['finished_products'] = int(st.session_state.inventory['finished_products'] * 0.95)
        
        # Natural demand variation (±10%)
        st.session_state.demand = int(st.session_state.demand * random.uniform(0.9, 1.1))
        
        # Calculate KPIs
        total_inventory_value = (
            st.session_state.inventory['raw_materials'] * 10 +
            st.session_state.inventory['api'] * 50 +
            st.session_state.inventory['finished_products'] * 200
        )
        
        sold_products = min(st.session_state.inventory['finished_products'], st.session_state.demand)
        otif = sold_products / st.session_state.demand if st.session_state.demand > 0 else 1
        
        # Update KPIs
        st.session_state.kpis['inventory_turnover'].append(sold_products / (st.session_state.inventory['finished_products'] + 0.1))
        st.session_state.kpis['otif'].append(otif)
        st.session_state.kpis['costs'].append(total_inventory_value)
        
        # Update financials
        revenue = sold_products * 300
        st.session_state.kpis['revenue'].append(revenue)
        st.session_state.money += revenue
        st.session_state.inventory['finished_products'] -= sold_products
    
    # Reset simulation
    if st.button("Reset Simulation 🔄"):
        st.session_state.initialized = False
        st.experimental_rerun()

# Main area - divided into three columns
col1, col2, col3 = st.columns([1, 1, 1])

# Column 1: Supply Chain Management
with col1:
    st.header("💼 Supply Chain Management")
    
    # Display current status
    st.subheader(f"🗓️ Week: {st.session_state.week}")
    st.metric("💰 Available Budget", f"${st.session_state.money:,}")
    st.metric("📊 Market Demand", f"{st.session_state.demand} units")
    
    # Inventory management
    st.subheader("📦 Inventory Levels")
    st.metric("🧪 Raw Materials", st.session_state.inventory['raw_materials'])
    st.metric("⚗️ API", st.session_state.inventory['api'])
    st.metric("💊 Finished Products", st.session_state.inventory['finished_products'])
    
    # Manufacturing decisions
    st.subheader("🏭 Production Decisions")
    
    raw_to_api = st.slider("Convert Raw Materials to API", 0, st.session_state.inventory['raw_materials'], 100)
    api_to_finished = st.slider("Convert API to Finished Products", 0, st.session_state.inventory['api'], 50)
    
    # Purchasing decisions
    st.subheader("🛒 Purchasing Decisions")
    raw_materials_to_buy = st.slider("Purchase Raw Materials", 0, 5000, 100)
    
    if st.button("Execute Decisions ✅"):
        # Check if can afford raw materials
        raw_material_cost = raw_materials_to_buy * 10
        if raw_material_cost <= st.session_state.money:
            # Update inventory based on manufacturing decisions
            st.session_state.inventory['raw_materials'] -= raw_to_api
            st.session_state.inventory['api'] += int(raw_to_api * 0.8)  # 80% conversion efficiency
            
            st.session_state.inventory['api'] -= api_to_finished
            st.session_state.inventory['finished_products'] += int(api_to_finished * 0.9)  # 90% conversion efficiency
            
            # Update inventory based on purchasing decisions
            st.session_state.inventory['raw_materials'] += raw_materials_to_buy
            st.session_state.money -= raw_material_cost
            
            st.success("Decisions executed successfully! 🎉")
        else:
            st.error("Insufficient funds to purchase raw materials! 💸")

# Column 2: Events and Analytics
with col2:
    st.header("📈 Events & Analytics")
    
    # Display events
    st.subheader("⚠️ Supply Chain Events")
    if st.session_state.events:
        for event in st.session_state.events[-5:]:
            st.info(event)
    else:
        st.write("No events yet 👍")
    
    # Display KPIs
    st.subheader("🎯 Key Performance Indicators")
    
    if len(st.session_state.kpis['inventory_turnover']) > 0:
        avg_inventory_turnover = sum(st.session_state.kpis['inventory_turnover']) / len(st.session_state.kpis['inventory_turnover'])
        avg_otif = sum(st.session_state.kpis['otif']) / len(st.session_state.kpis['otif'])
        
        st.metric("Inventory Turnover", f"{avg_inventory_turnover:.2f}", 
                  delta=f"{st.session_state.kpis['inventory_turnover'][-1] - avg_inventory_turnover:.2f}" if len(st.session_state.kpis['inventory_turnover']) > 1 else None)
        
        st.metric("On-Time In-Full (OTIF)", f"{avg_otif:.1%}", 
                  delta=f"{st.session_state.kpis['otif'][-1] - avg_otif:.1%}" if len(st.session_state.kpis['otif']) > 1 else None)
        
        # Profit calculation
        if len(st.session_state.kpis['revenue']) > 0:
            total_revenue = sum(st.session_state.kpis['revenue'])
            initial_money = 1000000
            profit = st.session_state.money - initial_money
            st.metric("🤑 Profit/Loss", f"${profit:,}", delta=profit)
    else:
        st.write("No KPI data yet. Run the simulation to generate data. ⏳")

# Column 3: Visualization
with col3:
    st.header("📊 Supply Chain Visualization")
    
    if len(st.session_state.history) > 1:
        # Prepare data for charts
        weeks = [h['week'] for h in st.session_state.history]
        demand_data = [h['demand'] for h in st.session_state.history]
        inventory_data = {
            'Raw Materials': [h['inventory']['raw_materials'] for h in st.session_state.history],
            'API': [h['inventory']['api'] for h in st.session_state.history],
            'Finished Products': [h['inventory']['finished_products'] for h in st.session_state.history]
        }
        
        # Demand vs. Inventory Chart
        st.subheader("Demand vs. Finished Product Inventory")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(weeks, demand_data, marker='o', label='Demand')
        ax.plot(weeks, inventory_data['Finished Products'], marker='s', label='Finished Products')
        ax.set_xlabel('Week')
        ax.set_ylabel('Units')
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)
        
        # Inventory Levels Chart
        st.subheader("Inventory Levels Over Time")
        fig, ax = plt.subplots(figsize=(10, 6))
        for name, data in inventory_data.items():
            ax.plot(weeks, data, marker='o', label=name)
        ax.set_xlabel('Week')
        ax.set_ylabel('Units')
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)
        
        # Financial Performance
        if len(st.session_state.kpis['revenue']) > 0:
            st.subheader("Financial Performance")
            fig, ax = plt.subplots(figsize=(10, 6))
            revenue_data = [0] + st.session_state.kpis['revenue']  # Add 0 for initial week
            costs_data = [0] + st.session_state.kpis['costs']  # Add 0 for initial week
            
            # Ensure arrays are the same length as weeks
            if len(revenue_data) < len(weeks):
                revenue_data = revenue_data + [0] * (len(weeks) - len(revenue_data))
            if len(costs_data) < len(weeks):
                costs_data = costs_data + [0] * (len(weeks) - len(costs_data))
                
            ax.bar(weeks, revenue_data, label='Revenue')
            ax.plot(weeks, costs_data, 'r-', marker='s', label='Inventory Cost')
            ax.set_xlabel('Week')
            ax.set_ylabel('USD ($)')
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)
    else:
        st.write("Run the simulation for at least 2 weeks to see visualizations. ⏳")

# Instructions and discussion section at the bottom
st.header("🤔 Group Discussion")
st.markdown("""
### ❓ Discussion Questions:
1. How did your decisions affect the entire supply chain?
2. What strategies worked well for managing unexpected events?
3. Which KPIs were most important to track for success?
4. How would you improve your approach in a second run?

### ✅ Key Learnings:
- Observe how inventory levels at one stage affect other stages
- Note the financial impact of different supply chain decisions
- Consider the trade-offs between inventory levels and service levels (OTIF)
- Evaluate risk mitigation strategies for supply chain disruptions
""")
