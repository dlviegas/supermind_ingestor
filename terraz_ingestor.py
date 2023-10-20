import pandas as pd
from pathlib import Path
import re
import io
from utils import request_latlong

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
        self.leads_files = [x.__str__() for x in Path('./data/terraz/leads/').glob('*')]

    def treat_files(self, file_path):
        with open(file_path, 'r', encoding='latin-1') as file:
             lines = file.readlines()
             line_remover = [x for x in lines if re.search('^([0-9]|ID)', x)]
        return io.StringIO(''.join(line_remover))

    def read_file(self, file_bytes):
        df = pd.read_csv(file_bytes, sep=r'\t', encoding='latin-1', on_bad_lines='skip')

        return df

    def eng_vars(self, df):
        dum = pd.get_dummies(df['Etapa'])
        df_final = pd.concat([df, dum], axis=1)
        df_final['Criado'] = (pd.Timestamp('2023-10-01') - pd.to_datetime(df.Criado, format='%d/%m/%Y %H:%M')).dt.days
        dum_imob = pd.get_dummies(df_final['Imobiliária: Geradora do lead [!]'])
        df_final = pd.concat([df_final, dum_imob], axis=1)
        df_final = df_final.query('Terraz == True or Brognoli == True')
        dum_canal = pd.get_dummies(df_final['Canal [!]'])
        df_final = pd.concat([df_final, dum_canal], axis=1)
        dum_motiv = pd.get_dummies(df_final['Motivo de descarte [!]'])
        df_final = pd.concat([df_final, dum_motiv], axis=1)
        dum_vend = pd.get_dummies(df_final['Pré-vendedor [!]'])
        df_final = pd.concat([df_final, dum_vend], axis=1)
        df_final['Data e hora da visita [!]'] = pd.to_datetime(df_final['Data e hora da visita [!]'], format='%d/%m/%Y %H:%M', errors='coerce')
        df_final['dia'] = df_final['Data e hora da visita [!]'].dt.day
        df_final['mes'] = df_final['Data e hora da visita [!]'].dt.month
        df_final['ano'] = df_final['Data e hora da visita [!]'].dt.year
        df_final['dia_da_semana'] = df_final['Data e hora da visita [!]'].dt.day_of_week

        season = (df_final['Data e hora da visita [!]'].dt.month % 12 + 3) // 3

        seasons = {
            1: 'Winter',
            2: 'Spring',
            3: 'Summer',
            4: 'Autumn'
        }

        df_final['season'] = season.map(seasons)
        df_final['hora_visita'] = df_final['Data e hora da visita [!]'].dt.hour
        df_final['minuto_visita'] = df_final['Data e hora da visita [!]'].dt.minute
        df_final['periodo_visita'] = df_final['hora_visita'].apply(periodo_do_dia)
        df_final.drop(['Imobiliária: Geradora do lead [!]', 'Canal [!]', 'Motivo de descarte [!]', 'Pré-vendedor [!]',
                       'Data e hora da visita [!]'],
                      axis=1, inplace=True)
        df_final['cep3'] = df_final['CEP [!]'].apply(lambda x: str(x)[:3])
        return df_final

    def main(self):
        leads_df = pd.DataFrame()

        for file_path in self.leads_files:
            file_bytes = self.treat_files(file_path)
            aux_df = self.read_file(file_bytes)
            aux_df = self.eng_vars(aux_df)
            leads_df = pd.concat([leads_df, aux_df])

        print('FIM')


if __name__ == "__main__":
    ing = TerrazIngestor()
    ing.main()
