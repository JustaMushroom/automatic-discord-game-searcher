from threading import Thread, Event
from queue import Queue
from tkinter import Tk, ttk
from time import sleep as wait
from loggingFramework import Logger
import requests
import json
import sys

logger = Logger()

def handle_exception(etype, value, traceback):
	logger.logException(value)
	quit()

sys.excepthook = handle_exception

skuKey = "primary_sku_id"

logger.logInfo("Getting games list")
datajson = requests.get("https://discordapp.com/api/v6/applications/detectable").json()

logger.logInfo("Building Interface")
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
	logger.logInfo("Starting...")
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

def cancelSearch():
	btn["state"] = "normal"
	root.title("Searching Discord for games... Cancelled")
	s_term_event.set()

def updateGUI(in_queue, in_event, term_event_in):
	logger.logInfo("[Update]: Starting...", True)
	while True:
		is_set = in_event.wait(10)

		if is_set:
			try:
				lb0text = in_queue.get()
				lb1text = in_queue.get()
				lb2text = in_queue.get()
				pbvalue = in_queue.get()

				lb0.config(text = lb0text)
				lb1.config(text = lb1text)
				lb2.config(text = lb2text)
				pb["value"] = pbvalue

				in_event.clear()
			except Exception as e:
				logger.logException(e)
				s_term_event.set()
				term_event_in.set()

		if term_event_in.is_set() is True:
			logger.logInfo("[Update]: Terminating...", True)
			return



def search(queue_out, event_out, term_event_out, term_event_in):
	logger.logInfo("[Search]: Starting...", True)
	maxItems = len(datajson)
	cItem = 1
	workingSKUS = []
	SKUCount = 0

	queue_out.put("Checked {} out of {} games".format("0", len(datajson)))
	queue_out.put("Starting")
	queue_out.put("Please wait...")
	queue_out.put(0)
	event_out.set()

	#root.update()

	wait(2)
	for item in datajson:
		try:
			while True:
				r = requests.get("https://discordapp.com/api/v6/store/published-listings/skus/{}".format(item[skuKey]))
				if r.status_code == 404:
					break
				elif r.status_code == 200:
					workingSKUS.append(item)
					break
				elif r.status_code == 429:
					wait(10)
					continue
				else:
					break
				SKUCount += 1

		except KeyError:
			pass
		except Exception as e:
			logger.logException(e)
		cItem += 1

		while not queue_out.empty():
			pass
		queue_out.put("Checked {} out of {} games".format(cItem - 1, len(datajson)))
		queue_out.put("Checking {}".format(item["name"]))
		queue_out.put("{} SKU IDs have been checked and I've found {} working SKUs so far".format(SKUCount, len(workingSKUS)))
		queue_out.put(cItem - 1)
		event_out.set()

		wait(1)
		if term_event_in.is_set():
			logger.logInfo("[Search]: Terminating...", True)
			term_event_out.set()
			return

	listString = []

	for item in workingSKUS:
		listString.append("{} : https://discord.com/store/skus/{}".format(item["name"], item[skuKey]))

	logger.logInfo("Writing to file...")
	with open("output.txt", "w") as outputfile:
		outputfile.write("\n".join(listString))

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

logger.logInfo("Interface built, starting main loop!")
root.mainloop()
