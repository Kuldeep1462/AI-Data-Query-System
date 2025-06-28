"use client"

/**
 * Query Context
 * Manages global state for query operations and results
 */

import { createContext, useContext, useReducer } from "react"

// Initial state for our query system
const initialState = {
  currentQuery: "",
  isLoading: false,
  results: null,
  error: null,
  queryHistory: [],
  activeTab: "text", // 'text', 'table', 'chart'
}

// Action types for our reducer
const ActionTypes = {
  SET_QUERY: "SET_QUERY",
  SET_LOADING: "SET_LOADING",
  SET_RESULTS: "SET_RESULTS",
  SET_ERROR: "SET_ERROR",
  ADD_TO_HISTORY: "ADD_TO_HISTORY",
  SET_ACTIVE_TAB: "SET_ACTIVE_TAB",
  CLEAR_RESULTS: "CLEAR_RESULTS",
}

// Reducer function to manage state changes
function queryReducer(state, action) {
  switch (action.type) {
    case ActionTypes.SET_QUERY:
      return {
        ...state,
        currentQuery: action.payload,
        error: null, // Clear any previous errors
      }

    case ActionTypes.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload,
      }

    case ActionTypes.SET_RESULTS:
      return {
        ...state,
        results: action.payload,
        isLoading: false,
        error: null,
      }

    case ActionTypes.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        isLoading: false,
        results: null,
      }

    case ActionTypes.ADD_TO_HISTORY:
      return {
        ...state,
        queryHistory: [
          action.payload,
          ...state.queryHistory.slice(0, 9), // Keep only last 10 queries
        ],
      }

    case ActionTypes.SET_ACTIVE_TAB:
      return {
        ...state,
        activeTab: action.payload,
      }

    case ActionTypes.CLEAR_RESULTS:
      return {
        ...state,
        results: null,
        error: null,
        currentQuery: "",
      }

    default:
      return state
  }
}

// Create the context
const QueryContext = createContext()

// Custom hook to use the query context
export const useQuery = () => {
  const context = useContext(QueryContext)
  if (!context) {
    throw new Error("useQuery must be used within a QueryProvider")
  }
  return context
}

// Provider component
export const QueryProvider = ({ children }) => {
  const [state, dispatch] = useReducer(queryReducer, initialState)

  // Action creators for cleaner component code
  const actions = {
    setQuery: (query) => dispatch({ type: ActionTypes.SET_QUERY, payload: query }),
    setLoading: (loading) => dispatch({ type: ActionTypes.SET_LOADING, payload: loading }),
    setResults: (results) => dispatch({ type: ActionTypes.SET_RESULTS, payload: results }),
    setError: (error) => dispatch({ type: ActionTypes.SET_ERROR, payload: error }),
    addToHistory: (historyItem) => dispatch({ type: ActionTypes.ADD_TO_HISTORY, payload: historyItem }),
    setActiveTab: (tab) => dispatch({ type: ActionTypes.SET_ACTIVE_TAB, payload: tab }),
    clearResults: () => dispatch({ type: ActionTypes.CLEAR_RESULTS }),
  }

  const value = {
    ...state,
    ...actions,
  }

  return <QueryContext.Provider value={value}>{children}</QueryContext.Provider>
}
