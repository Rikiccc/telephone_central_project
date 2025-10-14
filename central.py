from data_structures.ChainHashMap import ChainHashMap
from data_structures.Trie import Trie
from data_structures.DynamicArray import DynamicArray
from data_structures.PopularityGraph import PopularityGraph

import threading
import time
import pickle
from datetime import datetime, timedelta
import random

PHONEBOOK_FILE = "phones.txt"
CALLS_FILE = "calls.txt"
BLOCKED_FILE = "blocked.txt"
SERIAL_FILE = "saved_state.pkl"

class PhoneBookEntry:
    def __init__(self, first_name = "", last_name = "", number = ""):
        self.first_name = first_name
        self.last_name = last_name
        self.number = number
    def to_tuple(self):
        return (self.first_name, self.last_name, self.number)
    def display(self):
        return f"{self.first_name} | {self.last_name} | {self.number}"

class CallRecord:
    def __init__(self,caller_number,callee_number,start_date,duration_time):
        self.caller_number = caller_number
        self.callee_number = callee_number
        self.start_date = start_date
        self.duration_time = duration_time
    def display(self):
        return f"{self.caller_number} | {self.callee_number} | {self.start_date} | {self.duration_time}"

class Central:
    def __init__(self):
        self.phonebook = ChainHashMap()
        self.calls = DynamicArray()
        self.blocked = set()
        self.trie_first_name = Trie()
        self.trie_last_name = Trie()
        self.trie_phone_number = Trie()
        self.popularity_graph = PopularityGraph()
        self.calls_by_number = ChainHashMap()
        self.calls_by_pair = ChainHashMap()
        self.stress_thread = None
        self.stress_event = threading.Event()
        self.stress_pause = threading.Event()
        self.stress_stats = {"generated":0, "accepted":0, "blocked":0, "total_duration":0.0}
        self.stress_lock = threading.Lock()

    def load_phonebook(self, path=PHONEBOOK_FILE):
        with open(path,encoding='utf-8') as file:
            next(file)
            for line in file:
                line = line.strip()
                if not line:
                    continue
                parts = [part.strip() for part in line.split(',')]
                if len(parts) == 2:
                    full_name = parts[0].strip()
                    number = parts[1].strip()
                    name_split = full_name.split(" ")
                    first_name = name_split[0].strip()
                    last_name = name_split[1].strip()
                e = PhoneBookEntry(first_name = first_name, last_name = last_name, number = number)
                if number:
                    self.phonebook[number] = e
                    self.trie_first_name.insert(first_name,number)
                    self.trie_last_name.insert(last_name,number)
                    self.trie_phone_number.insert(number,number)

    def load_blocked(self,path=BLOCKED_FILE):
        with open(path,encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                self.blocked.add(line)

    def load_calls(self,path=CALLS_FILE,limit=None):
        self.calls.clear()
        self.calls_by_number.clear()
        self.calls_by_pair.clear()
        with open(path,encoding='utf-8') as file:
            for idx,line in enumerate(file):
                if limit and idx>=limit:
                    break
                parts = [p.strip() for p in line.strip().split(",")]
                caller_number, callee_number, date_start, duration_time = parts[0].strip(),parts[1].strip(),parts[2].strip(),parts[3].strip()
                try:
                    start_date = datetime.strptime(date_start,"%d.%m.%Y %H:%M:%S")
                except:
                    start_date = datetime.now()
                try:
                    h,m,s = (int(x) for x in duration_time.split(":"))
                    duration = timedelta(hours=h,minutes=m,seconds=s)
                except:
                    duration = timedelta()
                record = CallRecord(caller_number,callee_number,start_date,duration)
                self.calls.append(record)
                pair_key = tuple(sorted([caller_number, callee_number]))
                if pair_key not in self.calls_by_pair:
                    self.calls_by_pair[pair_key] = DynamicArray()
                self.calls_by_pair[pair_key].append(record)
                for num in [caller_number, callee_number]:
                    if num not in self.calls_by_number:
                        self.calls_by_number[num] = DynamicArray()
                    self.calls_by_number[num].append(record)
                self.popularity_graph.record_call(caller_number,callee_number,record.duration_time.total_seconds())

    def save_state(self, path=SERIAL_FILE):
        data = {
            "phonebook": {k:v.to_tuple() for k,v in self.phonebook.items()},
            "blocked": list(self.blocked),
            "pop_graph": self.popularity_graph.serialize(),
            "calls": [ (call.caller_number,call.callee_number,call.start_date.strftime("%d.%m.%Y %H:%M:%S"), str(call.duration_time)) for call in self.calls]
        }
        with open(path, "wb") as f:
            pickle.dump(data, f)
            print("State successfully serialized!")

    def load_state(self, path=SERIAL_FILE):
        with open(path, "rb") as file:
            data = pickle.load(file)
        self.phonebook.clear()
        for num,tup in data.get("phonebook",{}).items():
            first,last,number = tup
            self.phonebook[num] = PhoneBookEntry(first,last,number)
            if first:
                self.trie_first_name.insert(first,num)
            if last:
                self.trie_last_name.insert(last,num)
            if number:
                self.trie_phone_number.insert(number,num)
        self.blocked = set(data.get("blocked",[]))
        self.popularity_graph.deserialize(data.get("pop_graph",{}))
        self.calls.clear()
        self.calls_by_number.clear()
        self.calls_by_pair.clear()
        for caller_number, callee_number, date_start, duration_time in data.get("calls",[]):
            try:
                start_date = datetime.strptime(date_start, "%d.%m.%Y %H:%M:%S")
            except:
                start_date = datetime.now()
            try:
                h,m,s = (int(x) for x in duration_time.split(":"))
                duration = timedelta(hours=h,minutes=m,seconds=s)
            except:
                duration = timedelta()
            record = CallRecord(caller_number,callee_number,start_date,duration)
            self.calls.append(record)
            pair_key = tuple(sorted([caller_number, callee_number]))
            if pair_key not in self.calls_by_pair:
                self.calls_by_pair[pair_key] = DynamicArray()
            self.calls_by_pair[pair_key].append(record)
            for num in [caller_number, callee_number]:
                if num not in self.calls_by_number:
                    self.calls_by_number[num] = DynamicArray()
                self.calls_by_number[num].append(record)
            self.popularity_graph.record_call(caller_number,callee_number,record.duration_time.total_seconds())
        print("State successfully loaded!")

    def nice_entry(self,number):
        if number in self.phonebook:
            e = self.phonebook[number]
            return f"{e.display()}"
        return number

    def suggest_similar_numbers(self,number,n=5):
        def similarity_score(number1,number2):
            score = abs(len(number1)-len(number2))
            for a,b in zip(number1,number2):
                if a!=b:
                    score +=1
            return score
        candidates = list(self.phonebook.keys())
        ranked = sorted(candidates,key=lambda x:similarity_score(number,x))
        return ranked[:n]

    def suggest_similar_names(self,name,n=5):
        def similarity_score(name1,name2):
            name1=name1.lower()
            name2=name2.lower()
            prefix_len=0
            for a,b in zip(name1,name2):
                if a==b:
                    prefix_len +=1
                else:
                    break
            diff = abs(len(name1)-len(name2))
            diff+=sum(1 for a,b in zip(name1,name2) if a !=b)
            score = diff - (prefix_len)
            return score
        candidates = [f"{contact.first_name} {contact.last_name}" for contact in self.phonebook.values()]
        ranked = sorted(candidates,key=lambda x:similarity_score(name,x))
        return ranked[:n]

    def is_blocked(self, number):
        return number in self.blocked

    def live_call(self,caller_number,callee_number):
        caller_number = caller_number.strip()
        callee_number = callee_number.strip()
        if caller_number=="" or callee_number=="":
            print("[!] You must enter both numbers.")
            return
        if self.is_blocked(caller_number) or self.is_blocked(callee_number):
            print("[!] Call rejected: one of the numbers is blocked.")
            return
        print(f"[i] Starting call: {self.nice_entry(caller_number)} -> {self.nice_entry(callee_number)}")
        start = datetime.now()
        stop_event = threading.Event()
        def waiter(evt):
            input("Press ENTER to end the call...........\n")
            evt.set()
        th = threading.Thread(target=waiter, args=(stop_event,), daemon=True)
        th.start()
        last_print = time.time()
        try:
            while not stop_event.is_set():
                time.sleep(0.2)
                now = time.time()
                if now - last_print >= 1.0:
                    elapsed = datetime.now() - start
                    print(f"Duration: {str(elapsed).split('.')[0]}", end="\r")
                    last_print = now
        except KeyboardInterrupt:
            stop_event.set()
        end = datetime.now()
        dur = end - start
        record = CallRecord(caller_number, callee_number, start, dur)
        self.calls.append(record)
        pair_key = tuple(sorted([caller_number, callee_number]))
        if pair_key not in self.calls_by_pair:
            self.calls_by_pair[pair_key] = DynamicArray()
        self.calls_by_pair[pair_key].append(record)
        for num in [caller_number, callee_number]:
            if num not in self.calls_by_number:
                self.calls_by_number[num] = DynamicArray()
            self.calls_by_number[num].append(record)
        self.popularity_graph.record_call(caller_number,callee_number,record.duration_time.total_seconds())
        print("\n--- CALL INFORMATION ---")
        print(f"Caller number: {self.nice_entry(caller_number)}")
        print(f"Callee number: {self.nice_entry(callee_number)}")
        print(f"Call started at: {start.strftime('%d.%m.%Y %H:%M:%S')}")
        print(f"Call duration: {str(dur).split('.')[0]}")
        print("---------------------")
        with open("calls.txt", "a", encoding="utf-8") as file:
            file.write(f"{caller_number},{callee_number},{start.strftime('%d.%m.%Y %H:%M:%S')},{str(dur).split('.')[0]}\n")

    def simulate_calls_from_file(self,path=CALLS_FILE,limit=2000):
        count = 0
        with open(path,encoding='utf-8') as file:
            for line in file:
                if limit and count>=limit:
                    break
                parts = [part.strip() for part in line.strip().split(",")]
                caller_number, callee_number, date_start, duration_time = parts[0], parts[1], parts[2], parts[3]
                try:
                    start_date = datetime.strptime(date_start, "%d.%m.%Y %H:%M:%S")
                except:
                    start_date = datetime.now()
                try:
                    h,m,s = (int(x) for x in duration_time.split(":"))
                    duration = timedelta(hours=h, minutes=m, seconds=s)
                except:
                    duration = timedelta()
                record = CallRecord(caller_number,callee_number,start_date,duration)
                if self.is_blocked(caller_number) or self.is_blocked(callee_number):
                    print("[!] Call rejected: one of the numbers is blocked.")
                else:
                    self.calls.append(record)
                    pair_key = tuple(sorted([caller_number, callee_number]))
                    if pair_key not in self.calls_by_pair:
                        self.calls_by_pair[pair_key] = DynamicArray()
                    self.calls_by_pair[pair_key].append(record)
                    for num in [caller_number, callee_number]:
                        if num not in self.calls_by_number:
                            self.calls_by_number[num] = DynamicArray()
                        self.calls_by_number[num].append(record)
                    self.popularity_graph.record_call(caller_number,callee_number,record.duration_time.total_seconds())
                    print(f"[i] Starting call: {self.nice_entry(record.caller_number)} -> {self.nice_entry(record.callee_number)}")
                    print(f"{record.caller_number} -> {record.callee_number} | {record.start_date} | {record.duration_time}")
                count+=1

    def show_history_1(self,number):
        records = sorted(self.calls_by_number.get(number, []), key=lambda r: r.start_date)
        if not records:
            print("NO CALL HISTORY FOR THIS NUMBER!")
            return
        for record in records:
            role = "caller" if record.caller_number == number else "callee"
            other = record.callee_number if record.caller_number == number else record.caller_number
            print(f"{record.start_date.strftime('%d.%m.%Y %H:%M:%S')} | {role} {number} <-> {other} | {str(record.duration_time).split('.')[0]}")

    def show_history_2(self,number1,number2):
        key = tuple(sorted([number1,number2]))
        records = sorted(self.calls_by_pair.get(key, []), key=lambda r: r.start_date)
        if not records:
            print("NO CALL HISTORY BETWEEN THESE TWO NUMBERS!")
            return
        for record in records:
            role = f"{record.caller_number}->{record.callee_number}"
            print(f"{record.start_date.strftime('%d.%m.%Y %H:%M:%S')} | {role} | {str(record.duration_time).split('.')[0]}")

    def search_by_first(self,q,limit=50):
        nums = self.trie_first_name.prefix_numbers(q, limit=limit)
        sorted_nums = sorted(list(nums), key=lambda n: -self.popularity_graph.get_score(n))
        return sorted_nums[:limit]

    def search_by_last(self, q, limit=200):
        nums = self.trie_last_name.prefix_numbers(q, limit=limit)
        sorted_nums = sorted(list(nums), key=lambda n: -self.popularity_graph.get_score(n))
        return sorted_nums[:limit]

    def search_by_phone(self, pref, limit=200):
        nums = self.trie_phone_number.prefix_numbers(pref, limit=limit)
        sorted_nums = sorted(list(nums), key=lambda n: -self.popularity_graph.get_score(n))
        return sorted_nums[:limit]

    def autocomplete(self,prefix,kind="first",limit=20):
        if kind == "first":
            numbers =  self.trie_first_name.prefix_numbers(prefix,limit=200)
        elif kind == "last":
            numbers = self.trie_last_name.prefix_numbers(prefix,limit=200)
        else:
            numbers = self.trie_phone_number.prefix_numbers(prefix,limit=200)
        numbers_sorted = sorted(list(numbers), key=lambda n: -self.popularity_graph.get_score(n))
        return numbers_sorted[:limit]

    def print_pop_graph(self, limit=10):
        self.popularity_graph.show_all()
        print(f"\nTop {limit} most popular numbers:")
        scores = self.popularity_graph.top_n(limit)
        for i, (number, score) in enumerate(scores, 1):
            contact = self.phonebook.get(number)
            name = f"{contact.first_name} | {contact.last_name} | {contact.number}" if contact else number
            print(f"{i}) {name} score={score}")

    def start_stress_test(self,duration_seconds=60,target_calls=1000):
        if self.stress_thread and self.stress_thread.is_alive():
            print("Stress test is already running.")
            return
        nums = list(self.phonebook.keys())
        if not nums:
            print("No numbers in phonebook for stress test!")
            return
        self.stress_event.clear()
        self.stress_pause.clear()
        self.stress_stats = {"generated":0,"accepted":0,"blocked":0,"total_duration":0.0}
        def worker():
            start_time = time.time()
            end_time = start_time + duration_seconds
            calls_generated = 0
            while time.time() < end_time and calls_generated < target_calls and not self.stress_event.is_set():
                while self.stress_pause.is_set() and not self.stress_event.is_set():
                    time.sleep(0.1)
                caller_number = random.choice(nums)
                callee_number = random.choice(nums)
                if caller_number == callee_number:
                    continue
                if random.random() < 0.9:
                    dur_secs = random.randint(1,300)
                else:
                    dur_secs = random.randint(300,3600)
                start_date = datetime.now()
                dur_td = timedelta(seconds=dur_secs)
                with self.stress_lock:
                    self.stress_stats["generated"]+=1
                if self.is_blocked(caller_number) or self.is_blocked(callee_number):
                    with self.stress_lock:
                        self.stress_stats["blocked"]+=1
                else:
                    record = CallRecord(caller_number,callee_number, start_date, dur_td)
                    self.calls.append(record)
                    pair_key = tuple(sorted([caller_number, callee_number]))
                    if pair_key not in self.calls_by_pair:
                        self.calls_by_pair[pair_key] = DynamicArray()
                    self.calls_by_pair[pair_key].append(record)
                    for num in [caller_number, callee_number]:
                        if num not in self.calls_by_number:
                            self.calls_by_number[num] = DynamicArray()
                        self.calls_by_number[num].append(record)
                    self.popularity_graph.record_call(caller_number,callee_number,dur_secs)
                    with self.stress_lock:
                        self.stress_stats["accepted"]+=1
                        self.stress_stats["total_duration"]+=dur_secs
                calls_generated += 1
                time.sleep(duration_seconds / max(1,target_calls)*0.5)
            print("[i] Stress test thread finished.")
            self.stress_report()
            input("Press ENTER to return to the MENU")
        self._stress_thread = threading.Thread(target=worker, daemon=True)
        self._stress_thread.start()
        print("[i] Stress test started: duration", duration_seconds, "s, target", target_calls, "calls.")

    def pause_stress_test(self):
        if not hasattr(self, "_stress_thread") or not self._stress_thread.is_alive():
            print("Stress test is not active.")
            return
        self.stress_pause.set()
        print("Stress test paused.")

    def resume_stress_test(self):
        if not hasattr(self, "_stress_thread") or not self._stress_thread.is_alive():
            print("Stress test is not active.")
            return
        self.stress_pause.clear()
        print("Stress test resumed.")

    def stop_stress_test(self):
        if not self.stress_thread or not self.stress_thread.is_alive():
            print("Stress test is not active.")
            return
        self.stress_event.set()
        self.stress_thread.join(timeout=5)
        print("Stress test stopped.")

    def stress_report(self):
        with self.stress_lock:
            gen = self.stress_stats.get("generated",0)
            acc = self.stress_stats.get("accepted",0)
            blk = self.stress_stats.get("blocked",0)
            total_dur = self.stress_stats.get("total_duration",0.0)
        avg_dur = (total_dur/acc) if acc>0 else 0.0
        top5 = self.popularity_graph.top_n(5)
        print("----- Stress test report -----")
        print("Generated:", gen)
        print("Accepted:", acc)
        print("Blocked:", blk)
        print("Average duration (s):", f"{avg_dur:.2f}")
        print("Top 5 most popular (score):")
        for i,(num,score) in enumerate(top5, start=1):
            print(f"{i}) {self.nice_entry(num)} -> score={score:.2f}")
        print("-"*25)
