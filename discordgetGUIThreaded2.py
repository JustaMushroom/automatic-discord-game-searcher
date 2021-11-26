from threading import Thread, Event
from queue import Queue
from tkinter import Tk, ttk
from time import sleep as wait
import requests
import json

#file = open("data.txt", "r", encoding="utf8")
#file = open("gameslist.json", "r", encoding="utf8")
#data = file.read()

#data = requests.get("https://discordapp.com/api/v6/applications/detectable").json()

#skuKey = "primarySkuId"
skuKey = "primary_sku_id"

#datajson = json.loads(data)
datajson = requests.get("https://discordapp.com/api/v6/applications/detectable").json()

root = Tk()
root.title("Search Discord for games!")
root.geometry('400x250+1000+300')

lb0 = ttk.Label(root, text="{} games to check. Estimated time: {} minutes".format(len(datajson), round((len(datajson) * 1) / 60, 2)))
lb0.pack()
lb1 = ttk.Label(root, text="Checked {} out of {} games".format("0", len(datajson)))
lb1.pack()
lb2 = ttk.Label(root, text="Press Start to begin searching")
lb2.pack()
pb = ttk.Progressbar(root, maximum=len(datajson), mode="determinate")
pb.pack(expand=True)

info_queue = Queue()
info_event = Event()
term_event = Event()
s_term_event = Event()

def start():
	global updateThread
	global searchT
	s_term_event.clear()
	btn["state"] = "disabled"
	root.title("Searching Discord for games...")

	updateThread = Thread(target=updateGUI, args=(info_queue, info_event, term_event))
	searchT = Thread(target=search, args=(info_queue, info_event, term_event, s_term_event))

	updateThread.start()
	wait(0.1)
	searchT.start()
	#wait(2)
	#root.after(2000, cbtn.config(state = "normal"))

def cancelSearch():
	btn["state"] = "normal"
	root.title("Searching Discord for games... Cancelled")
	s_term_event.set()

def updateGUI(in_queue, in_event, term_event_in):
	print("[Update]: Starting...")
	while True:
		is_set = in_event.wait(10)

		if is_set:
			lb0text = in_queue.get()
			lb1text = in_queue.get()
			lb2text = in_queue.get()
			pbvalue = in_queue.get()

			lb0.config(text = lb0text)
			lb1.config(text = lb1text)
			lb2.config(text = lb2text)
			pb["value"] = pbvalue

			in_event.clear()

		if term_event_in.is_set() is True:
			print("[Update]: Terminating...")
			return



def search(queue_out, event_out, term_event_out, term_event_in):
	print("[Search]: Starting...")
	maxItems = len(datajson)
	cItem = 1
	workingSKUS = []
	SKUCount = 0

	#lb0.config(text="checked {} out of {} games".format("0", len(datajson)))
	queue_out.put("Checked {} out of {} games".format("0", len(datajson)))
	#lb1.config(text="Starting...")
	queue_out.put("Starting")
	queue_out.put("Please wait...")
	queue_out.put(0)
	event_out.set()

	#root.update()

	wait(2)
	for item in datajson:
		#print("[ {} / {}] Attempting {}...".format(cItem, maxItems, item["name"]))
		try:
			#print("[ {} / {}] Found {}: {}".format(cItem, maxItems, skuKey, item[skuKey]))
			r = requests.get("https://discordapp.com/api/v6/store/published-listings/skus/{}".format(item[skuKey]))
			if r.status_code == 404:
				#print("[ {} / {}] Discord: SKU Not Found".format(cItem, maxItems))
				pass
			elif r.status_code == 200:
				workingSKUS.append(item)
			else:
				#print("[ {} / {}] Discord: Unknown Response: {}".format(cItem, maxItems, r.status_code))
				pass
			SKUCount += 1

		except KeyError:
			pass
		cItem += 1

		while not queue_out.empty():
			pass
		#lb0.config(text="checked {} out of {} games".format(cItem - 1, len(datajson)))
		queue_out.put("Checked {} out of {} games".format(cItem - 1, len(datajson)))
		#lb1.config(text="Checking {}".format(item["name"]))
		queue_out.put("Checking {}".format(item["name"]))
		#lb2.config(text="Found {} working SKUs so far".format(len(workingSKUS)))
		queue_out.put("{} SKU IDs have been checked and I've found {} working SKUs so far".format(SKUCount, len(workingSKUS)))
		queue_out.put(cItem - 1)
		#root.update()
		event_out.set()

		wait(1)
		if term_event_in.is_set():
			print("[Search]: Terminating...")
			term_event_out.set()
			return
		#root.after(1000, None)

	listString = []

	for item in workingSKUS:
		listString.append("{} : https://discord.com/store/skus/{}".format(item["name"], item[skuKey]))

	#print("A total of {} working SKUs were found, a list is below:\n\n{}".format(len(workingSKUS), "\n".join(listString)))

	outputfile = open("output.txt", "w")
	outputfile.write("\n".join(listString))

	#lb1.config(text="Completed! Please check the console.")
	#lb2.config(text="Found {} working SKUs".format(len(workingSKUS)))
	queue_out.put(lb0["text"])
	queue_out.put("Completed! Please check the new output.txt file")
	queue_out.put("Found {} working SKUs".format(len(workingSKUS)))
	queue_out.put(pb["value"])
	event_out.set()

	term_event_out.set()

btn = ttk.Button(root, text="Start", command=start)
btn.pack()
cbtn = ttk.Button(root, text="Cancel", command=cancelSearch)
cbtn["state"] = "disabled"
cbtn.pack()

root.mainloop()