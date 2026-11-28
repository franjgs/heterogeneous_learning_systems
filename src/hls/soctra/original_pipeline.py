"""Vendored SOCTRA preprocessing functions from the upstream source.
Source: SoC_WP4 main @ 486d5b174f38c897d1adeafdde998142074a1cd1.
Only load, preprocessing, dynamic uniformization, and their direct helpers
are included. Trailing whitespace was trimmed; function logic is unchanged.
There is no runtime dependency on SoC_WP4.
"""

import logging
import os
import re
from datetime import datetime
import numpy as np
import pandas as pd
from pandas.api.types import is_string_dtype
logger = logging.getLogger(__name__)

def schedule_24x7_8x5(fecha_str: datetime):
    """Get the scheduler variable.

    Args:
        fecha_str (datetime): _description_

    Returns:
        bool str: "8x5" or "24x7"
    """
    # Datetime format
    fecha_str = fecha_str.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    fecha = datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Define the cutoff date
    fecha_corte = pd.Timestamp("2023-09-01 00:00:00")

    dia_semana = fecha.weekday()
    hora = fecha.hour
    # Check the schedule
    if fecha < fecha_corte:
        if 0 <= dia_semana <= 3 and 8 <= hora < 18:
            return "8x5"
        elif dia_semana == 4 and 8 <= hora < 15:
            return "8x5"
        else:
            return "24x7"
    else:
        if 0 <= dia_semana <= 4 and 8 <= hora < 22:
            return "8x5"
        else:
            return "24x7"

def func_load_data(
        data_path,
        weight_path,
        alarms_get_labels_colname = "reportado",
        alarms_label_colname = "Label",
        alarms_timestamp_colname = "@timestamp0",
        alarms_time_format = "%Y-%m-%d %H:%M:%S",
        feats2drop=[],
):
#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    logger.info("  * Importing alarms dataframe from: {}".format(data_path))
    df_alarms = pd.read_csv(data_path, low_memory=False)
    df_alarms.drop(feats2drop, axis=1, inplace=True)
    df_alarms[alarms_timestamp_colname] = pd.to_datetime(
        df_alarms[alarms_timestamp_colname], format = alarms_time_format
    )
    logger.info("    Alarms loaded : {}".format(df_alarms.shape))

    if weight_path in df_alarms.columns:
        df_alarms["weight"] = df_alarms[weight_path]
    elif os.path.exists(weight_path):
        logger.info(
            " Importing weights dataframe from: {}".format(weight_path)
        )
        df_weights = pd.read_csv(weight_path, low_memory=False)
        logger.info("    Weights loaded : {}".format(df_weights.shape))

        logger.info("  * Adding the weight column")

        dict_weights ={}
        for n_tram in range(df_weights.shape[0]):
            id_tram = df_weights.loc[n_tram,"tramitador"]
            for col in df_weights.columns[1:]:
                dict_weights[(id_tram,col)]  = df_weights.loc[n_tram,col]

        df_alarms["weight"] = (
            df_alarms[["tramitador","proyecto"]]
            .apply(tuple,axis=1)
            .map(dict_weights)
        )

    else:
        raise Exception("Weight path is not a column of dataframe or file")

    #--------------------------------------------------------------------------
    #  Getting Labels
    #--------------------------------------------------------------------------
    logger.info("  * Including labels into the dataframe")
    # Ensuring that label_colnames are in a list
    if isinstance(alarms_get_labels_colname, str):
        alarms_get_labels_colname = [alarms_get_labels_colname]

    # Following indications from GMV
    df_alarms.loc[
        df_alarms["motivo_sla_otros"].str.contains("8x5")
        & (df_alarms["proyecto"] != "kring"),
        "escalada_procedimiento",
    ] = True
    for count_label, get_label_colname in enumerate(alarms_get_labels_colname):
        label_colname = alarms_label_colname + "%d"%(count_label)

        if get_label_colname == "escalada":
            labels = df_alarms["escalada_procedimiento"] + df_alarms["escalada_L2"]
            # Replace values in "target" column with False and True
            # df_alarms[alarms_label_colname] = df_alarms[alarms_get_labels_colname].replace({0: False, 1: True})
            df_alarms[label_colname] = labels.replace({0: False, 1: True})
        elif get_label_colname == "tipo_cierre_2":
            df_alarms[label_colname] = df_alarms[
                alarms_get_labels_colname
            ].replace(
                {
                    "confirmed incident": True,
                    "no impact": False,
                    "false positive": False,
                    "potential incident": True,
                }
            )
        elif get_label_colname in [
            "reportado",
            "escalada_L2",
            "escalada_procedimiento"
        ]:
            df_alarms[label_colname] = df_alarms[get_label_colname]

        # Getting labels to show statistics
        labels = df_alarms[label_colname]
        logger.info("    Included label %s"%(get_label_colname))
        logger.info(
            "    + Label with distribution : False %d / True %d (IR=%.3f)"
            %(
                labels.value_counts()[False],
                labels.value_counts()[True],
                labels.value_counts()[False]/labels.value_counts()[True],
            )
        )

    return df_alarms

def func_preprocessing(
        df_alarms,
        feats2lower=[],
        projects2drop=[],
        drop_titulo=[],
        dict_action_str=None,
        dict_srccountry=None,
        get_top=None,
        project_start_date=None,
        alarms_timestamp_colname = "@timestamp0",
        alarms_get_labels_colname = "escalada",
        alarms_label_colname="Label"
        ):
#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    logger.info("    Unprocessed alarms : {}".format(df_alarms.shape))
    #-- GENERATION OF "24x7_8x5_online"
    df_alarms["schedule_L1"] = df_alarms["@timestamp0"].apply(schedule_24x7_8x5)

    #-- LOWERCASE
    for col in feats2lower:
        # ----------------------------------------------------------------------
        # FIX: Comprobar explícitamente si el tipo de dato es adecuado para .str
        # Usamos is_string_dtype para manejar dtypes 'object', 'string', etc.
        # ----------------------------------------------------------------------
        if (is_string_dtype(df_alarms[col])) or (df_alarms[col].dtype == object):
            # Aplicar .str.lower() SÓLO si es una columna de string
            df_alarms[col] = df_alarms[col].str.lower()
        else:
            # Si el tipo es int64 (AlertLevel) o cualquier otro no-string,
            # lo ignoramos, manteniendo su valor original.
            logger.warning(
                f"Advertencia: Columna '{col}' (dtype: {df_alarms[col].dtype}) no es de tipo string y fue ignorada en lowercasing."
            )

    #-- fuente : removing prefixes
    #df_alarms["fuente"] = df_alarms["fuente"].str.removeprefix("ALERTS:")
    #df_alarms["fuente"] = df_alarms["fuente"].str.removeprefix("ALERTAS:")
    df_alarms.loc[df_alarms["fuente"].str.startswith("alertas:", na=False), "fuente"] = df_alarms["fuente"].str.replace("^alertas:", "alerts:",regex=True)
    # Reemplazar valores NaN con una cadena vacía, y a continuación, con "missing"
    df_alarms["fuente"] = df_alarms["fuente"].fillna("")

    #-- description: remove prefix (contained in use_case_id, e.g. [GMV_GL00013]) and initial whitespaces
    df_alarms["description"]=df_alarms["description"].str.split(pat="]").str[-1].str.strip()


    #-- url_str:
    # Reemplazar valores NaN con una cadena vacía
    df_alarms["url_str"] = df_alarms["url_str"].fillna("")


    #-- user_case_name:
    # Aplicar la función a cada fila
    df_alarms["use_case_in_others"] = df_alarms.apply(verificar_contenido, axis=1)
    # Reemplazar valores según la condición, manejando cadenas vacías y NaN
    df_alarms.loc[
        (df_alarms["use_case_id"] == "gmv_gl00440")
        & (
            df_alarms["use_case_name"].isna()
            | (df_alarms["use_case_name"] == "")
        ),
        "use_case_name",
    ] = "anomalies-new device on the system"
    df_alarms.loc[
        (df_alarms["use_case_id"] == "hoh_sp00003")
        & (
            df_alarms["use_case_name"].isna()
            | (df_alarms["use_case_name"] == "")
        ),
        "use_case_name",
    ] = "intrusions - ftp anonymous login attempt"
    df_alarms.loc[
        (df_alarms["use_case_id"] == "jac_sp00001")
        & (
            df_alarms["use_case_name"].isna()
            | (df_alarms["use_case_name"] == "")
        ),
        "use_case_name",
    ] = "anomalies - possible compromised account"
    df_alarms.loc[
        (df_alarms["use_case_id"] == "ken_gl00028")
        & (
            df_alarms["use_case_name"].isna()
            | (df_alarms["use_case_name"] == "")
        ),
        "use_case_name",
    ] = "malware - malware detection"
    df_alarms.loc[
        (df_alarms["use_case_id"] == "ken_gl00029")
        & (
            df_alarms["use_case_name"].isna()
            | (df_alarms["use_case_name"] == "")
        ),
        "use_case_name",
    ] = "malware - multiple malware detection same host"
    df_alarms.loc[
        (df_alarms["use_case_id"] == "ono_sp00035")
        & (
            df_alarms["use_case_name"].isna()
            | (df_alarms["use_case_name"] == "")
        ),
        "use_case_name",
    ] = "lucia - incidents report new ticket with investigation required"

    #-- titulo_investigacion: remove prefix (contained in use_case_id, e.g. [GMV_GL00013]) and initial whitespaces
    #df_alarms["titulo_investigacion"]=df_alarms["titulo_investigacion"].str.split(pat="]").str[-1].str.strip()

    replacements = {
        "Ã\x83\\u0083Ã\x82Â±": "ñ",
        "ã\x83\\u0083ã\x82â±": "ñ",  # Marce
        "Ã\x83\\u0083Ã\x82Âº": "u",
        "ã\x83\\u0083ã\x82âº": "u",  # Marce
        "Ã\x83\\u0083Ã\x82Â³": "o",
        "ã\x83\\u0083ã\x82â³": "o",  # Marce
        "Ã\x83\\u0083Ã\x82Â¡": "a",
        "ã\x83\\u0083ã\x82â¡": "a",  # Marce
        "Ã\x83\\u0083Ã\x82\\u0083Ã\x83\\u0083Ã\x82\\u0082Ã\x83\\u0082Ã\x82Â¡": "a",
        "ã\x83\\u0083ã\x82\\u0083ã\x83\\u0083ã\x82\\u0082ã\x83\\u0082ã\x82â¡": "a",  # Marce
    }

    df_alarms["titulo_investigacion"] = df_alarms[
        "titulo_investigacion"
    ].apply(lambda x: replace_chars(x, replacements))
    df_alarms = df_alarms.apply(actualizar_campos, axis=1)
    df_alarms["titulo_investigacion"] = df_alarms.apply(clean_title, axis=1)
    #df_alarms = df_alarms[~df_alarms["titulo_investigacion"].str.contains("LUCIA|CERT-EU", regex=True)]

    #-- action_str: translate "auditoría correcta"
    df_alarms.loc[
        df_alarms[
            df_alarms["action_str"].fillna("nada").str.contains("correcta")
        ].index,
        "action_str",
    ] = "audit success"
    df_alarms.loc[
        df_alarms[
            df_alarms["action_str"]
            .fillna("nada")
            .str.lower()
            .str.contains("error de audi")
        ].index,
        "action_str",
    ] = "audit failure"

    if dict_action_str == None:

        dict_action_str = {
            "blocked": "block",
            "dropped": "drop",
            "detected": "detect",
            "detection": "detect",
            "denied": "deny",
            "DENIED": "deny",
            "sucesso da auditoria": "audit success",
            "prevented (blocked)": "prevent",
            "user_login": "login",
            "policyedit": "policy",
            "passthrough": "pass",
            "server-rst": "reset-server",
        }

    for key in dict_action_str.keys():
        df_alarms["action_str"] = df_alarms["action_str"].replace(
            key, dict_action_str[key]
        )#, inplace=True)

    # Reemplazar los valores "none" con "missing"
    df_alarms["action_str"] = df_alarms["action_str"].replace("none", "")
    # Reemplazar las celdas vacías (incluyendo NaN) con "missing"
    #df_alarms["action_str"] = df_alarms["action_str"].replace("", "missing")
    df_alarms["action_str"] = df_alarms["action_str"].fillna("")

    #-- srccountry / dstcountry : normalization of values
    if dict_srccountry == None:
        dict_srccountry={
            "korea, republic of": "korea",
            "united": "united states",
        }

    for key in dict_srccountry.keys():
        df_alarms["srccountry"] = df_alarms["srccountry"].replace(
            key, dict_srccountry[key]
        )#, inplace=True)
        df_alarms["dstcountry"] = df_alarms["dstcountry"].replace(
            key, dict_srccountry[key]
        )#, inplace=True)

    df_alarms["srccountry"] = df_alarms["srccountry"].fillna("")
    df_alarms["dstcountry"] = df_alarms["dstcountry"].fillna("")

    # -- user_str
    df_alarms["user_str"] = df_alarms["user_str"].fillna("")

    #-- protocol_str
    df_alarms["protocol_str"] = df_alarms["protocol_str"].fillna("")

    #-- status_str
    df_alarms["status_str"] = df_alarms["status_str"].fillna("")

    #-- id_str
    # Reemplazar los valores "none" con "missing"
    df_alarms["id_str"] = df_alarms["id_str"].replace("none", "")
    df_alarms["id_str"] = df_alarms["id_str"].replace("-", "")
    df_alarms["id_str"] = df_alarms["id_str"].fillna("")

    #-- extra_data_str
    dict_extra_data_str = None
    if dict_extra_data_str == None:
        dict_extra_data_str={"anti-malware": "anti malware"}

    for key in dict_extra_data_str.keys():
        df_alarms["extra_data_str"] = df_alarms["extra_data_str"].replace(
            key, dict_extra_data_str[key]
        )#, inplace=True)

    # Reemplazar las celdas vacías (incluyendo NaN) con "missing"
    df_alarms["extra_data_str"] = df_alarms["extra_data_str"].fillna("")


    for text_titulo in drop_titulo:
        df_alarms = df_alarms[
            df_alarms["titulo_investigacion"].str.contains(text_titulo)
            ==False
        ]
        #df_alarms = df_alarms[df_alarms["titulo_investigacion"].str.contains("cert-eu")==False]

    for project in projects2drop:
        df_alarms = df_alarms[df_alarms["proyecto"]!=project]

    if get_top != None:
        project_count = df_alarms["proyecto"].value_counts()
        top_projects = list(project_count.index)[0:get_top]

        #top_projects = list(project_count.index)[0:get_top]
        top_projects = project_count.index.tolist()[0:get_top]

        list_idx = []

        for project in top_projects:
            list_idx += df_alarms.index[
                df_alarms["proyecto"]==project
            ].tolist()

        list_idx.sort()
        df_alarms = df_alarms.loc[list_idx]

    # Alarms with "Mailbox - " in "titulo_investigacion" are removed
    df_alarms = df_alarms[
        ~df_alarms["titulo_investigacion"]
        .str.contains("Mailbox -", na=False, case=False)
    ]

    if project_start_date != None:
        list_idx = []
        for project in project_start_date.keys():
            list_idx += df_alarms.index[
                (df_alarms["proyecto"]==project)
                & (
                    df_alarms[alarms_timestamp_colname]
                    <pd.to_datetime(project_start_date[project])
                )
            ].to_list()

        list_idx.sort()
        df_alarms = df_alarms.drop(list_idx)

    df_alarms.sort_values(by=alarms_timestamp_colname)
    df_alarms.reset_index(inplace=True, drop=True)

    logger.info("    Preprocessed alarms: {}".format(df_alarms.shape))
    # Ensuring that label_colnames are in a list
    if isinstance(alarms_get_labels_colname, str):
        alarms_get_labels_colname = [alarms_get_labels_colname]

    for count_label, get_label_colname in enumerate(alarms_get_labels_colname):
        label_colname = alarms_label_colname + "%d"%(count_label)

        # Alarms with severity "medium" do not scale in "24x7"
        # if alarms_get_labels_colname == "escalada":
        #     # df_alarms.loc[(df_alarms["severidad"] == "medium") & (df_alarms["24x7_8x5"] == "24x7"), "Label"] = False
        #     # df_alarms.loc[(df_alarms["severidad"] == "medium") & (df_alarms["schedule_L1"] == "24x7"), "Label"] = False
        #     df_alarms = df_alarms[~((df_alarms["severidad"] == "medium") & (df_alarms["schedule_L1"] == "24x7"))]

        labels = df_alarms[label_colname]
        logger.info("    Label %s"%(get_label_colname))
        logger.info(
            "      + Label with distribution : False %d / True %d (IR=%.3f)"
            %(
                labels.value_counts()[False],
                labels.value_counts()[True],
                labels.value_counts()[False]/labels.value_counts()[True],
            )
        )

    return df_alarms

def func_uniform(df, columns_uni=[], col_label_base = "Label", mode="majority",
                 weight_operator=False, weight_positive=1):
    """
    Applies label processing to pattern that are identical in the specified
    columns in a DataFrame and adjusts label weights based on the specified mode.

    Parameters:
    + df (pandas.DataFrame): The DataFrame to process.
    + columns_uni (list, optional): List of column names to apply uniform processing to.
       Defaults to an empty list.

    + col_label_base (str, optional): The base name of the label column in the DataFrame.
       Defaults to "Label".
    + mode (str, optional): The mode of processing for labels.
       Supported modes are "majority", "single", "last", "weighted_majority" and "dynamic"
       Defaults to "majority"
    + weight_operator (boolean): If True, labels are weigthed with operator experience
       Defaults to False
    + weight_positive (int, optional): The weight assigned to positive labels.
        Defaults to 1. Only applied with "weighted_majority" or "dynamic" mode

    In the "dynamic" mode, two columns are added to the dataframe: "OrdinalLabel"
    and "Ambiguous"

    Returns:
    pandas.DataFrame: The processed DataFrame with uniform processing applied
        to the specified columns and adjusted label weights.

    Raises:
    ValueError: If an unsupported mode is provided.

    """

    cols_label = df.columns[df.columns.str.startswith(col_label_base)].to_list()

    n_labels = len(cols_label)

    if isinstance(mode, list)==False:
        mode = [mode for x in range(n_labels)]
    if isinstance(weight_positive, list)==False:
        weight_positive = [weight_positive for x in range(n_labels)]

    logger.info("    Uniforming alarms labels in dataframe: {}".format(df.shape))

    for count_label, col_label in enumerate(cols_label):

        if mode[count_label] == "dynamic":
            # Assign the base values for "OrdinalLabel"
            df["OrdinalLabel"] = df[col_label].map({False: 0, True: 5})

            # Count the number of unique values in "Label" for each combination of features
            label_counts = df.groupby(columns_uni)[
                col_label
            ].nunique().reset_index()


            # Identify ambiguous patterns (more than one unique value in "Label")
            ambiguous_features = label_counts[
                label_counts[col_label] > 1
            ].drop(columns=[col_label])

            # Añadir una columna indicando si la fila es ambigua o no
            df["Ambiguous"] = df[
                columns_uni
            ].merge(ambiguous_features, how="left", indicator=True)["_merge"] == "both"

            # Filtrar solo las filas ambiguas del DataFrame original
            df_ambiguous = df.merge(
                ambiguous_features, on=columns_uni, how="inner"
            )

            # Contar el número total de patrones por cada combinación de características ambiguas
            pattern_counts_ambiguous = df_ambiguous.groupby(
                columns_uni
            ).size().reset_index(name="PatternCount")

            # Contar cuántas filas ambiguas tienen Label == True
            true_counts_ambiguous = df_ambiguous[
                df_ambiguous[col_label] == True
            ].groupby(columns_uni).size().reset_index(name="TrueCount")

            # Unir ambos conteos en un solo DataFrame
            aggregated_counts_ambiguous = pattern_counts_ambiguous.merge(
                true_counts_ambiguous, on=columns_uni, how="left"
            ).fillna(0)

            # Convertir TrueCount a entero
            aggregated_counts_ambiguous["TrueCount"] = aggregated_counts_ambiguous[
                "TrueCount"
            ].astype(int)

            # Cálculo del Imbalance Ratio por patrón
            aggregated_counts_ambiguous["IbRatio"] = (
                aggregated_counts_ambiguous["PatternCount"]
                -aggregated_counts_ambiguous["TrueCount"]
            )/aggregated_counts_ambiguous["TrueCount"]

            # Merge df with ambiguous_features to identify ambiguous patterns in df
            df = df.merge(
                ambiguous_features, on=columns_uni, how="left", indicator=True
            )

            # Filter only the ambiguous patterns
            df_ambiguous = df[df["_merge"] == "both"].copy()

            # Count label transitions for each ambiguous pattern
            df_ambiguous["transitions"] = df_ambiguous.groupby(
                columns_uni
            )[col_label].transform(lambda x: np.sum(x.diff().fillna(0) != 0))

            # Apply the LabelOrdinal rules in a vectorized way
            df_ambiguous["OrdinalLabel"] = np.where(
                df_ambiguous["transitions"] == 1,
                np.where(df_ambiguous.groupby(columns_uni)[col_label].transform("first"), 1, 4),  # If it starts as True → 1, if it starts as False → 4
                np.where(aggregated_counts_ambiguous.set_index(columns_uni)["IbRatio"].reindex(df_ambiguous.set_index(columns_uni).index) < weight_positive[count_label], 3, 2)
            )

            # Update the original dataframe with the computed values
            df.update(df_ambiguous[["OrdinalLabel"]])

            # Remove the auxiliary "_merge" column
            df.drop(columns=["_merge"], inplace=True)

            # Update "Label" based on "LabelOrdinal"
            df[col_label] = np.where(df["OrdinalLabel"] <= 2, False, True)

        else:
            # Group by columns
            grouped = df.replace(
                "",np.nan
            ).fillna("fillingNaN").groupby(columns_uni)

            for name, group in grouped:
                if group.shape[0] > 1:
                    if mode[count_label] == "last":
                        # For each group, set "col_label" to the value in the last row of that group
                        last_value = group.iloc[-1][col_label]
                        df.loc[group.index, col_label] = last_value
                    elif mode[count_label] == "single":
                        # For each group, set "col_label" to True if a single alarm exists
                        maj_value = group[col_label].mean() >= 0.0
                        df.loc[group.index, col_label] = maj_value
                    elif mode[count_label] == "majority":
                        # For each group, set "col_label" by the majority labels
                        if weight_operator:
                            maj_value = (
                                (group[col_label].astype(float)-1)*group["weight"]
                                 + group[col_label].astype(float)*group["weight"]
                                ).mean() >= 0.0
                        else:
                            maj_value = group[col_label].mean() >= 0.5

                        df.loc[group.index, col_label] = maj_value

                    elif mode[count_label] == "weighted_majority":
                        # As the previous one, but positive labels are weighted
                        if weight_operator:
                            maj_value = ((group[col_label].astype(float)-1)*group["weight"]
                                         + weight_positive[count_label]*group[col_label].astype(float)*group["weight"]).mean() >= 0.0
                        else:
                            threshold = 1/weight_positive[count_label]
                            maj_value = group[col_label].mean() >= threshold

                        df.loc[group.index, col_label] = maj_value

                    else:
                        raise TypeError("Unexpected value for 'mode'")

        labels = df[col_label]
        logger.info(
            "      * Label with distribution : False %d / True %d (IR=%.3f)"
            %(
                labels.value_counts()[False],
                labels.value_counts()[True],
                labels.value_counts()[False]/labels.value_counts()[True],
            )
        )

    return df

def replace_chars(text, replacements):
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def clean_title(row):
    title = row["titulo_investigacion"]
    case_id = row["use_case_id"]
    case_name = row["use_case_name"]

    if pd.isna(title) or pd.isna(case_id) or pd.isna(case_name):
        return title

    # Buscar todos los textos entre corchetes y paréntesis
    matches = re.findall(r"\[(.*?)\]", title) + re.findall(r"\((.*?)\)", title)

    for match in matches:
        if match in case_id or match in case_name:
            title = title.replace(f"[{match}]", "").replace(f"({match})", "")

    return title.strip()

def actualizar_campos(row):
    if pd.isna(row["use_case_id"]):
        # Encontrar la cadena dentro de corchetes
        inicio = row["titulo_investigacion"].find("[")
        fin = row["titulo_investigacion"].find("]")
        if inicio != -1 and fin != -1:
            # Obtener la cadena a eliminar y actualizar case_use_id
            cadena_eliminar = row["titulo_investigacion"][inicio : fin + 1]
            # row['use_case_id'] = '[' + cadena_eliminar[1:-1].split(',')[0] + ']'
            row["use_case_id"] = cadena_eliminar[1:-1].split(",")[0]
            # Eliminar la cadena del título de investigación
            row["titulo_investigacion"] = (
                row["titulo_investigacion"]
                .replace(cadena_eliminar, "")
                .strip()
            )
    return row

def verificar_contenido(row):
    use_case = (
        str(row["use_case_name"]).lower()
        if pd.notnull(row["use_case_name"])
        else ""
    )
    titulo = (
        str(row["titulo_investigacion"]).lower()
        if pd.notnull(row["titulo_investigacion"])
        else ""
    )
    alert = (
        str(row["alert_name"]).lower() if pd.notnull(row["alert_name"]) else ""
    )
    return (use_case in titulo) or (use_case in alert)
