import pandas as pd
from pathlib import Path
import re
import io
# from utils import request_latlong

def periodo_do_dia(x):
    if (x >= 0) and (x < 8):
        return 'Madrugada'
    elif (x >= 8) and (x < 12):
        return 'Manhã'
    elif (x >= 12) and (x < 18):
        return'Tarde'
    elif (x >= 18) and (x < 0) :
        return 'Noite'


class TerrazIngestor:
    def __init__(self):
        self.leads_files = [x.__str__() for x in Path('../data/terraz/leads/').glob('*.csv')]

    def treat_files(self, file_path):
        with open(file_path, 'r', encoding='latin-1') as file:
             lines = file.readlines()
             line_remover = [x for x in lines if re.search('^([0-9]|ID)', x)]
        return io.StringIO(''.join(line_remover))

    def read_file(self, file_bytes):
        df = pd.read_csv(file_bytes, sep=r'\t', encoding='latin-1', on_bad_lines='skip')

        return df

    def eng_vars(self, df):
        # dum = pd.get_dummies(df['Etapa'])
        # df_final = pd.concat([df, dum], axis=1)
        df_final = df
        df_final['criado_dias'] = (pd.Timestamp('2023-10-01') - pd.to_datetime(df.Criado, format='%d/%m/%Y %H:%M')).dt.days
        df_final = df_final[df_final['Imobiliária: Geradora do lead'].isin(['Terraz', 'Brognoli'])]
        # dum_imob = pd.get_dummies(df_final['Imobiliária: Geradora do lead'])
        # df_final = pd.concat([df_final, dum_imob], axis=1)
        # df_final = df_final.query('Terraz == True or Brognoli == True')
        # dum_canal = pd.get_dummies(df_final['Canal'])
        # df_final = pd.concat([df_final, dum_canal], axis=1)
        # dum_motiv = pd.get_dummies(df_final['Motivo de descarte'])
        # df_final = pd.concat([df_final, dum_motiv], axis=1)
        # dum_vend = pd.get_dummies(df_final['Pré-vendedor'])
        # df_final = pd.concat([df_final, dum_vend], axis=1)
        df_final['Criado'] = pd.to_datetime(df_final['Criado'], format='%d/%m/%Y %H:%M', errors='coerce')
        df_final['dia'] = df_final['Criado'].dt.day
        df_final['mes'] = df_final['Criado'].dt.month
        df_final['ano'] = df_final['Criado'].dt.year
        df_final['dia_da_semana'] = df_final['Criado'].dt.day_of_week

        season = (df_final['Criado'].dt.month % 12 + 3) // 3

        seasons = {
            1: 'Winter',
            2: 'Spring',
            3: 'Summer',
            4: 'Autumn'
        }

        df_final['season'] = season.map(seasons)
        df_final['hora_visita'] = df_final['Criado'].dt.hour
        df_final['minuto_visita'] = df_final['Criado'].dt.minute
        df_final['periodo_visita'] = df_final['hora_visita'].apply(periodo_do_dia)
        # df_final.drop(['Imobiliária: Geradora do lead', 'Canal', 'Motivo de descarte', 'Pré-vendedor',
        #                'Criado'],
        #               axis=1, inplace=True)
        df_final['cep3'] = df_final['CEP'].apply(lambda x: str(x)[:3])
        return df_final

    def missing_cleaner(self, df, n_miss=400000):
        miss_serie = df.isna().sum()
        miss_list = miss_serie[miss_serie < n_miss].index.to_list()

        return df[miss_list]

    def column_names_fixer(self, df):
        df.columns = df.columns.str.replace(r'\s+\[\!\]\s*', '', regex=True)

        return df

    def main(self, eng, write_file=False):
        leads_df = pd.DataFrame()

        for file_path in self.leads_files:
            file_bytes = self.treat_files(file_path)
            aux_df = self.read_file(file_bytes)
            leads_df = pd.concat([leads_df, aux_df])
        if eng:
            leads_df = self.missing_cleaner(leads_df)
            leads_df = self.column_names_fixer(leads_df)
            leads_df = self.eng_vars(leads_df)
        if write_file:
            leads_df.to_csv('../data/terraz/processed_leads/leads.csv', index=False)
        return leads_df
        # print('FIM')


if __name__ == "__main__":
    ing = TerrazIngestor()
    ing.main()
