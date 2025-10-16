# ☎️ Telephone Switchboard Simulation

This project simulates a **telephone switchboard system**, featuring:
- A searchable phonebook,
- Call logging and analysis,
- Contact lookup by name or number,
- Popularity tracking of frequently called numbers,
- Live call simulation,
- Performance (stress) testing of the system.

It is written in **Python** and uses several **custom data structures** (`ChainHashMap`, `Trie`, `DynamicArray`, `Graph`) for efficient storage and retrieval.

---

## 🚀 Features

- **Phonebook Management:**  
  Load contacts from a text file and store them in a hash map and tries for fast prefix searches.
- **Call Simulation:**  
  Import and simulate calls from a log file or create a live call between two contacts.
- **Call History:**  
  Display full call history for a single number or between two specific numbers.
- **Autocomplete & Suggestions:**  
  Suggest similar names or phone numbers, and provide autocomplete for prefixes.
- **Popularity Graph:**  
  Analyze which numbers are most frequently involved in calls.
- **Serialization:**  
  Save and load the full system state using Python's `pickle`.
- **Stress Testing:**  
  Generate thousands of random calls to test performance and concurrency handling.

---

## 🧠 Data Structures Used

| Data Structure | Purpose |
|----------------|----------|
| `ChainHashMap` | Hash-based map for storing phonebook and call mappings. |
| `Trie` | Prefix tree for fast searching and autocompletion by name or number. |
| `DynamicArray` | Dynamic storage for call logs. |
| `PopularityGraph` | Graph structure for tracking and ranking popular numbers. |

---

## ⚙️ How to Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/telephone-switchboard.git
   cd telephone-switchboard


