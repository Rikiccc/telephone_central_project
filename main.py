from central import Central

def menu():
    print("-"*30)
    print("----- PHONE SWITCHBOARD -----")
    print("1. LIVE CALL")
    print("2. SIMULATION FROM FILE")
    print("3. CALL HISTORY FOR NUMBER")
    print("4. CALL HISTORY BETWEEN TWO NUMBERS")
    print("5. SEARCH CONTACTS")
    print("6. DID YOU MEAN")
    print("7. AUTOCOMPLETE")
    print("8. SAVE STATE (SERIALIZATION)")
    print("9. LOAD STATE (SERIALIZATION)")
    print("10. SHOW TOP POPULAR NUMBERS")
    print("11. SHOW POPULARITY GRAPH")
    print("12. START STRESS TEST")
    print("13. PAUSE STRESS TEST")
    print("14. RESUME STRESS TEST")
    print("15. STOP STRESS TEST")
    print("X. EXIT APPLICATION")
    print("-"*30)

def main():
    c = Central()
    c.load_phonebook()
    c.load_calls(limit=50000)
    c.load_blocked()
    while True:
        menu()
        option = input("Choose an option: ").strip()
        if option == "1":
            while True:
                caller_number = input("Enter caller number: ").strip()
                if caller_number in c.phonebook:
                    break
                print("[!] Number not found in contacts")
                sug = c.suggest_similar_numbers(caller_number)
                if sug:
                    print("Did you mean:", ", ".join(sug))
            while True:
                callee_number = input("Enter callee number: ").strip()
                if callee_number in c.phonebook:
                    break
                print("[!] Number not found in contacts")
                sug = c.suggest_similar_numbers(callee_number)
                if sug:
                    print("Did you mean:", ", ".join(sug))
            c.live_call(caller_number, callee_number)
        elif option == "2":
            path = "calls.txt"
            c.simulate_calls_from_file(path=path)
        elif option == "3":
            while True:
                number = input("Enter number: ").strip()
                if number in c.phonebook:
                    break
                print("[!] Number not found in contacts")
                sug = c.suggest_similar_numbers(number)
                if sug:
                    print("Did you mean:", ", ".join(sug))
            c.show_history_1(number)
        elif option == "4":
            while True:
                number1 = input("Enter first number: ").strip()
                if number1 in c.phonebook:
                    break
                print("[!] Number not found in contacts")
                sug = c.suggest_similar_numbers(number1)
                if sug:
                    print("Did you mean:", ", ".join(sug))
            while True:
                number2 = input("Enter second number: ").strip()
                if number2 in c.phonebook:
                    break
                print("[!] Number not found in contacts")
                sug = c.suggest_similar_numbers(number2)
                if sug:
                    print("Did you mean:", ", ".join(sug))
            c.show_history_2(number1,number2)
        elif option == "5":
            print("Choose search filter: ")
            print("1. FIRST NAME")
            print("2. LAST NAME")
            print("3. PHONE NUMBER")
            search_filter = input("Choice: ").strip()
            if search_filter == "1":
                name = input("Search.... : ").strip()
                result = c.search_by_first(name,limit=1000)
                for i,num in enumerate(result,start=1):
                    print(f"{i}) {c.nice_entry(num)}  [score={c.popularity_graph.get_score(num):.1f}]")
                input("Press ENTER to return to menu...")
            if search_filter == "2":
                forname = input("Search.... : ").strip()
                result = c.search_by_last(forname,limit=1000)
                for i,num in enumerate(result,start=1):
                    print(f"{i}) {c.nice_entry(num)}  [score={c.popularity_graph.get_score(num):.1f}]")
                input("Press ENTER to return to menu...")
            if search_filter == "3":
                number = input("Search.... : ").strip()
                result = c.search_by_phone(number,limit=1000)
                for i,num in enumerate(result,start=1):
                    print(f"{i}) {c.nice_entry(num)}  [score={c.popularity_graph.get_score(num):.1f}]")
                input("Press ENTER to return to menu...")
            else:
                print("Unknown option!")
        elif option=="6":
            filter = input("Suggestions for (1) number (2) name: ").strip()
            if filter=="1":
                number = input("Enter number: ").strip()
                print("Suggestions:", c.suggest_similar_numbers(number))
            elif filter=="2":
                name = input("Enter first/last name: ").strip()
                print("Suggestions:", c.suggest_similar_names(name))
            else:
                print("Unknown option!")
        elif option == "x":
            print("Thank you for using the application!")
            break
        elif option=="7":
            pref = input("Prefix: ").strip()
            kind = input("Type (first/last/phone): ").strip() or "first"
            if kind == "first":
                kind_b = "first"
            elif kind == "last": 
                kind_b = "last"
            elif kind == "phone":
                kind_b = "phone"
            comps = c.autocomplete(pref, kind=kind_b)
            for comp in comps:
                print(c.nice_entry(comp), f"[score={c.popularity_graph.get_score(comp):.1f}]")
            input("Press ENTER to return to menu...")
        elif option=="8":
            c.save_state()
        elif option=="9":
            c.load_state()
        elif option=="10":
            n = eval(input("Enter how many top numbers to show: ").strip())
            for i,(num,score) in enumerate(c.popularity_graph.top_n(n), start=1):
                print(f"{i}) {c.nice_entry(num)} score={score:.1f}")
        elif option=="11":
            c.print_pop_graph(limit=100)
        elif option=="12":
            sec = input("Duration (seconds): ").strip()
            calls = input("Number of calls: ").strip()
            sec = int(sec) if sec else 60
            calls = int(calls) if calls else 1000
            c.start_stress_test(duration_seconds=sec, target_calls=calls)
        elif option=="13":
            c.pause_stress_test()
        elif option=="14":
            c.resume_stress_test()
        elif option=="15":
            c.stop_stress_test()
            c.stress_report()
        else:
            print("Unknown option!")
        
if __name__ == '__main__':
    main()
