import pandas as pd
import glob
from unidecode import unidecode
import chardet
from utils.treatment import *

class BlocoIngestor:
    """Class for ingestor of Bloco company"""
    def __init__(self):
        __file_path = './data/Bloco/'
        self.files_w_headers = ['./data/Bloco/base soft opening.csv', './data/Bloco/captação.csv', './data/Bloco/comunicação digital.csv',
                                './data/Bloco/crecigeral2.csv', './data/Bloco/crecigeral3.csv', './data/Bloco/Emailing Secovi Imobi Summit Preview 2021.csv',
                                './data/Bloco/imob2quente.csv', './data/Bloco/inscritos bloco+.csv', './data/Bloco/lista1imobs quentes.csv',
                                './data/Bloco/sidenir crm.csv', './data/Bloco/TODAS-STARTUPS-LINKLAB-_1_.csv']
        self.df = pd.DataFrame()



    def reader(self):
        self.df = pd.concat(map(self.csv_reader, self.files_w_headers))

    def csv_reader(self, file_path):
        if 'xlsx' in file_path:
            pd.read_excel(file_path)
        rawdata = open(file_path, 'rb').read()
        df = pd.read_csv(file_path, encoding=chardet.detect(rawdata)['encoding'], sep=';')
        df.columns = [x.upper() for x in df.columns]
        df = df.loc[:,~df.columns.str.contains('^UNNAMED', case=False)]
        for column in df.columns:
            df = df.rename(columns={column: unidecode(column)})
            if df[unidecode(column)].dtype == 'str':
                df[unidecode(column)] = df[unidecode(column)].apply(lambda x: unidecode(x))

        return df

    def treatments(self):

        for x in self.df.TELEFONE:
            number_treat(x)

    def main(self):
        self.reader()
        self.treatments()
        print(self.df.head())


if __name__ == '__main__':
    bloco=BlocoIngestor()
    bloco.main()
