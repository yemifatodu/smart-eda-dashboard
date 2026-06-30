import streamlit as st
import pandas as pd
import copy

class UndoManager:
    def __init__(self):
        self.history = []
        self.current_index = -1
        self.max_history = 50
    
    def push_state(self, df, action):
        # Save current state
        state = {
            'data': copy.deepcopy(df),
            'action': action,
            'timestamp': pd.Timestamp.now()
        }
        
        # Remove any future states if we're in the middle
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        
        # Add new state
        self.history.append(state)
        self.current_index = len(self.history) - 1
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.current_index -= 1
    
    def undo(self):
        if self.current_index > 0:
            self.current_index -= 1
            return self.history[self.current_index]['data'], True
        return None, False
    
    def redo(self):
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            return self.history[self.current_index]['data'], True
        return None, False
    
    def get_history_summary(self):
        return [
            f"{i+1}. {state['action']} ({state['timestamp'].strftime('%H:%M:%S')})"
            for i, state in enumerate(self.history[:self.current_index + 1])
        ]

def show():
    st.markdown('<h1 class="main-header">↩️ Undo/Redo Manager</h1>', unsafe_allow_html=True)
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
        return
    
    # Initialize undo manager
    if 'undo_manager' not in st.session_state:
        st.session_state.undo_manager = UndoManager()
        # Save initial state
        st.session_state.undo_manager.push_state(st.session_state.data, "Initial data load")
    
    manager = st.session_state.undo_manager
    df = st.session_state.data
    
    st.markdown("### 🎯 Data Operations with Undo/Redo")
    
    # Operation selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        operation = st.selectbox(
            "Select Operation",
            ["Add Column", "Remove Column", "Filter Rows", "Sort Data", "Add Calculation"]
        )
    
    with col2:
        st.markdown("### ⏪ Quick Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("↩️ Undo (Ctrl+Z)", use_container_width=True):
                data, success = manager.undo()
                if success:
                    st.session_state.data = data
                    st.success("✅ Undo successful!")
                    st.rerun()
                else:
                    st.warning("Nothing to undo")
        with col2:
            if st.button("↪️ Redo (Ctrl+Y)", use_container_width=True):
                data, success = manager.redo()
                if success:
                    st.session_state.data = data
                    st.success("✅ Redo successful!")
                    st.rerun()
                else:
                    st.warning("Nothing to redo")
    
    st.markdown("---")
    
    # Operation details
    if operation == "Add Column":
        col_name = st.text_input("New Column Name", "new_column")
        formula = st.text_input("Formula (e.g., df['Sales'] * 2)", "df['Sales'] * 2")
        
        if st.button("➕ Add Column", type="primary"):
            try:
                new_data = df.copy()
                new_data[col_name] = eval(formula)
                manager.push_state(df, f"Added column: {col_name}")
                st.session_state.data = new_data
                st.success(f"✅ Added column '{col_name}'")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    elif operation == "Remove Column":
        cols_to_remove = st.multiselect("Select columns to remove", df.columns.tolist())
        
        if st.button("🗑️ Remove Columns", type="primary"):
            if cols_to_remove:
                new_data = df.drop(columns=cols_to_remove)
                manager.push_state(df, f"Removed columns: {', '.join(cols_to_remove)}")
                st.session_state.data = new_data
                st.success(f"✅ Removed columns: {', '.join(cols_to_remove)}")
                st.rerun()
    
    elif operation == "Filter Rows":
        selected_col = st.selectbox("Select column to filter", df.columns.tolist())
        
        if df[selected_col].dtype in ['object', 'category']:
            values = st.multiselect("Select values to keep", df[selected_col].unique().tolist())
            if st.button("🔍 Apply Filter"):
                new_data = df[df[selected_col].isin(values)]
                manager.push_state(df, f"Filtered on {selected_col}")
                st.session_state.data = new_data
                st.success(f"✅ Filtered to {len(new_data):,} rows")
                st.rerun()
        else:
            min_val, max_val = st.slider(
                "Range",
                float(df[selected_col].min()),
                float(df[selected_col].max()),
                (float(df[selected_col].min()), float(df[selected_col].max()))
            )
            if st.button("🔍 Apply Filter"):
                new_data = df[(df[selected_col] >= min_val) & (df[selected_col] <= max_val)]
                manager.push_state(df, f"Filtered {selected_col} between {min_val} and {max_val}")
                st.session_state.data = new_data
                st.success(f"✅ Filtered to {len(new_data):,} rows")
                st.rerun()
    
    elif operation == "Sort Data":
        sort_col = st.selectbox("Select column to sort", df.columns.tolist())
        ascending = st.checkbox("Ascending", True)
        
        if st.button("🔃 Sort Data"):
            new_data = df.sort_values(by=sort_col, ascending=ascending)
            manager.push_state(df, f"Sorted by {sort_col}")
            st.session_state.data = new_data
            st.success("✅ Data sorted!")
            st.rerun()
    
    elif operation == "Add Calculation":
        col_name = st.text_input("New Column Name", "calculated")
        calc_type = st.selectbox("Calculation Type", ["Sum", "Mean", "Max", "Min", "Standard Deviation"])
        calc_col = st.selectbox("Select column", df.select_dtypes(include=['number']).columns.tolist())
        
        if st.button("➕ Add Calculation"):
            new_data = df.copy()
            if calc_type == "Sum":
                new_data[col_name] = df[calc_col].sum()
            elif calc_type == "Mean":
                new_data[col_name] = df[calc_col].mean()
            elif calc_type == "Max":
                new_data[col_name] = df[calc_col].max()
            elif calc_type == "Min":
                new_data[col_name] = df[calc_col].min()
            elif calc_type == "Standard Deviation":
                new_data[col_name] = df[calc_col].std()
            
            manager.push_state(df, f"Added {calc_type} of {calc_col}")
            st.session_state.data = new_data
            st.success(f"✅ Added {calc_type} calculation")
            st.rerun()
    
    # History
    st.markdown("---")
    st.subheader("📋 History")
    
    history = manager.get_history_summary()
    if history:
        st.caption(f"Current state: {len(history)} steps")
        for item in history:
            st.text(item)
    else:
        st.info("No history yet")
    
    # Reset button
    if st.button("🗑️ Reset History"):
        st.session_state.undo_manager = UndoManager()
        st.session_state.undo_manager.push_state(st.session_state.data, "Reset")
        st.success("History reset!")
        st.rerun()
