import pandas as pd
import glob

class TerrazIngestor:
    def __init__(self):
        self.message_files = glob.glob('./data/terraz/messages/*')
        self.imoveis_files = glob.glob('./data/terraz/imoveis/*')
        self.leads_files = glob.glob('./data/leads/*')

    def read_messages(self):
        self.df_messages = pd.concat(map(lambda x: pd.read_csv(x, sep=';'), self.message_files))