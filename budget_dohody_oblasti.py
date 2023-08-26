# Програма працює довго і показує попередження, вле це не помилки
import pandas as pd
from pandas.tseries.offsets import MonthEnd
import random
import time
import re

def myReplace(dfr, trans_dict):
    for c_phrase in trans_dict:
        dfr = dfr.replace(c_phrase, trans_dict[c_phrase])
    return dfr

# Програма яка якось формує дані в нормальний вигляд (допоміг написати chatGPT)
def flatten_categories(category, parent_category='', level=1):
    flat_categories = []
    code = category['code']
    code_name = category['codeName']

    ancestors = get_ancestors(category)

    flat_categories.append({
        'Parent Category': parent_category,
        'Level': level,
        'Code': code,
        'Code Name': code_name,
        'Ancestors': ' > '.join(ancestors),
        'PeriodId': category['periodId'],
        'RozpisZmin': category['data']['rozpisZmin'],
        'KoshtorysZmin': category['data']['koshtorysZmin'],
        'DonePeriod': category['data']['donePeriod'],
        'CorrectionYearDonePercent': category['data']['correctionYearDonePercent']
    })

    subcategories = category.get('children', [])
    for subcategory in subcategories:
        flat_categories.extend(flatten_categories(subcategory, code_name, level + 1))

    return flat_categories

def get_ancestors(category):
    ancestors = []

    parent_category = category.get('Parent Category')
    if parent_category:
        ancestors.append(parent_category)
        ancestors.extend(get_ancestors(parent_category))

    return ancestors


# Словник для перекладу на англійську
dict_en = {'Вінницька': 'Vinnytsia',
           'Волинська': 'Volyn',
           'Дніпропетровська': 'Dnipropetrovsk',
           'Донецька': 'Donetsk',
           'Житомирська': 'Zhytomyr',
           'Закарпатська': 'Zakarpattia',
           'Запорізька': 'Zaporizhzhia',
           'Івано-Франківська': 'Ivano-Frankivsk',
           'Київ': 'Kyiv city',
           'Київська': 'Kyiv',
           'Кіровоградська': 'Kirоvohrad',
           'Луганська': 'Luhansk',
           'Львівська': 'Lviv',
           'Миколаївська': 'Mykolaiv',
           'Одеська': 'Odesa',
           'Полтавська': 'Poltava',
           'Рівненська': 'Rivne',
           'Сумська': 'Sumy',
           'Тернопільська': 'Ternopil',
           'Харківська': 'Kharkiv',
           'Херсонська': 'Kherson',
           'Хмельницька': 'Khmelnytskyi',
           'Черкаська': 'Cherkasy',
           'Чернівецька': 'Chernivtsi',
           'Чернігівська': 'Chernihiv',
           'Податкові надходження': 'Tax revenues',
           'Неподаткові надходження': 'Non-tax revenues',
           'Рентна плата та плата за використання інших природних ресурсів': 'Rent and fees for the use of other natural resources',
           'Внутрішні податки на товари та послуги': 'Domestic taxes on goods and services',
           'Збори на паливно-енергетичні ресурси': 'Fees for fuel and energy resources',
           'Доходи від власності та підприємницької діяльності': 'Income from property and business activities',
           'Адміністративні збори та платежі, доходи від некомерційної господарської діяльності': 'Administrative fees and charges, income from non-commercial economic activities',
           'Інші податки та збори': 'Other taxes and fees',
           'Податки на доходи, податки на прибуток, податки на збільшення ринкової вартості': 'Income tax, profit tax, market value increment tax',
           'Рентна плата за спеціальне використання води': 'Rent for special water use',
           'Рентна плата за користування надрами': 'Rent for subsoil use',
           'Рентна плата за транспортування': 'Rent for transportation',
           'Акцизний податок з вироблених в Україні підакцизних товарів (продукції)': 'Excise tax on excisable goods (products) produced in Ukraine',
           'Акцизний податок з ввезених на митну територію України підакцизних товарів (продукції)': 'Excise tax on excise goods (products) imported into the customs territory of Ukraine',
           'Збір у вигляді цільової надбавки до діючого тарифу на природний газ для споживачів усіх форм власності, нарахований до 1 січня 2016 року': 'Fee in the form of surcharge to the effective natural gas tariff for consumers of all forms of ownership, charged until January 1, 2016',
           'Інші надходження': 'Other revenues',
           'Плата за надання адміністративних послуг': 'Fee for the provision of administrative services',
           'Податок на додану вартість з вироблених в Україні товарів (робіт, послуг) з урахуванням бюджетного відшкодування': 'Value-added tax on goods (works, services) produced in Ukraine, taking into account budget compensation',
           'Збір за забруднення навколишнього природного середовища': 'Fee for environmental pollution',
           'Податок на прибуток підприємств': 'Corporate income tax',
           'Частина чистого прибутку (доходу) державних або комунальних унітарних підприємств та їх об\'єднань, що вилучається до відповідного бюджету, та дивіденди (дохід), нараховані на акції (частки) господарських товариств, у статутних капіталах яких є державна або комунальна власність': 'Part of the net profit (income) of state or municipal unitary enterprises and their associations, which is withdrawn to the relevant budget, and dividends (income) accrued on shares (shares) of business entities in the authorized capital of which there is state or municipal property',
           'Рентна плата за користування надрами загальнодержавного значення': 'Rent for the use of subsoil of national importance',
           'Рентна плата за спеціальне використання води для потреб гідроенергетики': 'Rent for the special use of water for hydropower needs',
           'Рентна плата за користування надрами континентального шельфу і в межах виключної (морської) економічної зони': 'Rent for the use of subsoil within the continental shelf and within the exclusive (marine) economic zone',
           'Рентна плата за користування надрами для видобування нафти': 'Rent for the use of subsoil for oil extraction',
           'Рентна плата за користування надрами для видобування природного газу': 'Rent for the use of subsoil for natural gas extraction',
           'Рентна плата за користування надрами для видобування газового конденсату': 'Rent for the use of subsoil for gas condensate extraction',
           'Рентна плата за користування надрами для видобування нафти, що нарахована до 1 січня 2018 року, погашення податкового боргу та повернення  помилково або надміру сплачених сум до 31 грудня 2017 року': 'Rent for the use of subsoil for oil extraction, charged until January 1, 2018, repayment of tax debt, and return of erroneously or excessively paid amounts until December 31, 2017',
           'Рентна плата за користування надрами для видобування природного газу, що нарахована до 1 січня 2018 року, погашення податкового боргу та повернення  помилково або надміру сплачених сум до 31 грудня 2017 року': 'Rent for the use of subsoil for natural gas extraction, charged until January 1, 2018, repayment of tax debt, and return of erroneously or excessively paid amounts until December 31, 2017',
           'Рентна плата за користування надрами для видобування газового конденсату, що нарахована до 1 січня 2018 року, погашення податкового боргу та повернення  помилково або надміру сплачених сум до 31 грудня 2017 року': 'Rent for the use of subsoil for gas condensate extraction, charged until January 1, 2018, repayment of tax debt, and return of erroneously or excessively paid amounts until December 31, 2017',
           'Рентна плата за транспортування нафти та нафтопродуктів магістральними нафтопроводами та нафтопродуктопроводами територією України': 'Rent for transportation of oil and oil products by main oil pipelines and oil product pipelines through the territory of Ukraine',
           'Електрична енергія': 'Electricity',
           'Пальне': 'Fuel',
           'Збір у вигляді цільової надбавки до діючого тарифу на природний газ для споживачів усіх форм власності, який справляється за поставлений природний газ споживачам на підставі укладених з ними договорів, нарахований до 1 січня 2016 року': 'Fee in the form of surcharge to the effective natural gas tariff for consumers of all forms of ownership, for the supplied natural gas based on contracts concluded with them, charged until January 1, 2016',
           'Збір у вигляді цільової надбавки до діючого тарифу на природний газ для споживачів усіх форм власності, який справляється за видобутий суб\'єктами господарювання та спожитий ними природний газ як паливо або сировина, нарахований до 1 січня 2016 року': 'Fee in the form of surcharge to the effective natural gas tariff for consumers of all forms of ownership, for the extracted natural gas used by economic entities as fuel or raw material, charged until January 1, 2016',
           'Штрафні санкції за порушення законодавства з питань забезпечення ефективного використання енергетичних ресурсів': 'Penalties for violation of the legislation in the issues of ensuring efficient use of energy resources',
           'Плата за експлуатацію газорозподільних систем або їх складових': 'Fee for the operation of gas distribution systems or their components',
           'Внески на регулювання, які сплачуються суб’єктами господарювання, що провадять діяльність у сферах енергетики та комунальних послуг, відповідно до статті 13 Закону України «Про Національну комісію, що здійснює державне регулювання у сферах енергетики та комунальних послуг»': 'Regulatory contributions paid by business entities operating in the energy and utilities sectors in accordance with Article 13 of the Law of Ukraine "On the National Energy and Utilities Regulatory Commission"',
           'Плата за ліцензії, видані Національною комісією, що здійснює державне регулювання у сферах енергетики та комунальних послуг': 'Fee for licenses issued by the National Energy and Utilities Regulatory Commission',
           'Збір за видачу спеціальних дозволів на користування надрами та кошти від продажу таких дозволів': 'Fee for the issuance of special permits for subsoil use and funds from the sale of such permits',
           'Надходження від погашення податкового боргу, в тому числі реструктуризованого або розстроченого (відстроченого), з податку на додану вартість (з урахуванням штрафних санкцій, пені та процентів, нарахованих на суму цього розстроченого (відстроченого) боргу), що сплачуються підприємствами електроенергетичної, нафтогазової, вугільної галузей, підприємствами, що надають послуги з виробництва, транспортування та постачання теплової енергії, підприємствами централізованого водопостачання та водовідведення': 'Revenue from the repayment of tax debts, including restructured or deferred debts, from value-added tax (including penalties, fines, and interest charged on the amount of such deferred debt) paid by enterprises in the electric power, oil and gas, coal industries, enterprises providing services for the production, transportation, and supply of heat energy, and enterprises of centralized water supply and wastewater disposal',
           'Надходження коштів від енергопідприємств до Державного фонду охорони навколишнього природного середовища': 'Funds received from energy companies to the State Environmental Protection Fund',
           'Рентна плата за транзитне транспортування трубопроводами природного газу територією України, що нарахована до 1 січня 2016 року': 'Rent payment for transit transportation of natural gas through pipelines across the territory of Ukraine charged until January 1, 2016',
           'Надходження від погашення податкового боргу, в тому числі реструктуризованого або розстроченого (відстроченого), з податку на прибуток підприємств (з урахуванням штрафних санкцій, пені та процентів, нарахованих на суму цього боргу), що склався станом на 1 січня 2018 року, який сплачується підприємствами електроенергетичної, нафтогазової, вугільної галузей': 'Revenue from the repayment of tax debts, including restructured or deferred debts, from corporate income tax (including penalties, fines, and interest charged on the amount of such debt) accrued as of January 1, 2018, paid by enterprises in the electric power, oil and gas, coal industries',
           'Надходження від підприємств електроенергетичної, нафтогазової, вугільної галузей дивідендів (доходу), нарахованих на акції (частки) господарських товариств, у статутних капіталах яких є державна власність, що залучаються до розрахунків на виконання положень частини другої статті 21 Закону України "Про Державний бюджет України на 2018 рік"': 'Revenue from enterprises of the electric power, oil and gas, coal industries of dividends (income) accrued on shares (shares) of business entities, in the authorized capital of which there is state property, involved in calculations for the implementation of the provisions of part two of Article 21 of the Law of Ukraine "On the State Budget of Ukraine for 2018"',
           'Податок на прибуток підприємств електроенергетичної, нафтогазової, вугільної галузей, що залучається до розрахунків на виконання положень частини другої статті 21 Закону України "Про Державний бюджет України на 2018 рік"': 'Income tax of enterprises of the electric power, oil and gas, coal industries involved in calculations in compliance with the provisions of part two of Article 21 of the Law of Ukraine "On the State Budget of Ukraine for 2018"',
           'Надходження від погашення податкового боргу, в тому числі реструктуризованого або розстроченого (відстроченого), із сплати частини чистого прибутку (доходу) державних унітарних підприємств та їх об’єднань, що вилучається до державного бюджету відповідно до закону (з урахуванням штрафних санкцій, пені та процентів, нарахованих на суму цього боргу), що склався станом на 1 січня 2018 року, який сплачується підприємствами електроенергетичної, нафтогазової, вугільної галузей': 'Revenue from the repayment of tax debts, including restructured or deferred debts, from the payment of part of the net profit (income) of state unitary enterprises and their associations, which is withdrawn to the state budget in accordance with the law (including penalties, fines, and interest charged on the amount of such debt) accrued as of January 1, 2018, paid by enterprises in the electric power, oil and gas, coal industries',
           'Плата за ліцензії на виробництво пального': 'Fee for licenses for fuel production',
           'Плата за ліцензії на право оптової торгівлі пальним': 'Fee for licenses for wholesale trade in fuel',
           'Плата за ліцензії на право роздрібної торгівлі пальним': 'Fee for licenses for retail trade in fuel',
           'Плата за ліцензії на право зберігання пального': 'Fee for licenses for fuel storage',
           'Плата за ліцензії, сертифікацію оператора системи передачі електричної енергії, оператора газотранспортної системи, видані/здійснену Національною комісією, що здійснює державне регулювання у сферах енергетики та комунальних послуг': 'Fee for licenses and certification of the operator of the electricity transmission system, the operator of the gas transmission system, issued/carried out by the National Commission for State Regulation of Energy and Utilities',
           'Надходження від сплати дивідендів (доходу), нарахованих на акції (частки) за результатами фінансово-господарської діяльності у 2019 році акціонерного товариства "Національна акціонерна компанія "Нафтогаз України"': 'Revenue from the payment of dividends (income) accrued on shares (stakes) based on the results of financial and economic activities in 2019 of Naftogaz of Ukraine JSC',
           'Рентна плата за користування надрами для видобування кам’яного вугілля коксівного та енергетичного': 'Rent payment for the use of subsoil for the extraction of coking and energy coal',
           'Рентна плата за спеціальне використання води без її вилучення з водних об’єктів для потреб гідроенергетики': 'Rent payment for the special use of water without its withdrawal from water bodies for the needs',
           }

bud_type = 'incomesLocal'  # Це якщо Доходи
fund = "TOTAL"  # Це якщо у вкладці "Фонд" вибрати "Разом" ( ще є варіанти "Спеціальний" і "Загальний")
region_code = [['АР Крим', '0110000000'], ['Вінницька', '0210000000'], ['Волинська', '0310000000'],
               ['Дніпропетровська', '0410000000'], ['Донецька', '0510000000'], ['Житомирська', '0610000000'],
               ['Закарпатська', '0710000000'], ['Запорізька', '0810000000'], ['Івано-Франківська', '0910000000'],
               ['Київська', '1010000000'], ['Кіровоградська', '1110000000'], ['Луганська', '1210000000'],
               ['Львівська', '1310000000'], ['Миколаївська', '1410000000'], ['Одеська', '1510000000'],
               ['Полтавська', '1610000000'], ['Рівненська', '1710000000'], ['Сумська', '1810000000'],
               ['Тернопільська', '1910000000'], ['Харківська', '2010000000'], ['Херсонська', '2110000000'],
               ['Хмельницька', '2210000000'], ['Черкаська', '2310000000'], ['Чернівецька', '2410000000'],
               ['Чернігівська', '2510000000'], ['Київ', '2600000000'], ['Севастополь', '2700000000']]
categories = ['11021900', '11022000', '13020300', '13030400', '13030700', '13030800', '13030900', '13031100',
              '13031200', '13031300', '13031500', '13080100', '13080200', '14021300', '14021900', '14031400',
              '14031900', '14060600', '17060100', '17060300', '19050100', '21010600', '21010700', '21011000',
              '21081200', '21081600', '21084000', '22011500', '22011500', '22012100', '22013100', '22013200',
              '22013300', '22013400']
# Додамо порожній DataFrame
df_result = pd.DataFrame()

y = input('Введіть рік останнього місяця потрібного діапазону: ')
m = input('Введіть останній місяць потрібного діапазону: ')
m_count = int(input('Введіть за скільки місяців потрібні дані: '))
# Дата першого дня останнього місяця
d1 = pd.to_datetime(f'{y}-{m}-01')
# Змінна d2 буде містити дату d1 - m_count місяців
d2 = d1 - pd.DateOffset(months=m_count - 1)
# Пройдемося по всіх перших днях місяців від d2 до d1
for d in pd.date_range(d2, d1, freq='MS'):
    year = d.year
    month = d.month
    print(f'Місяць: {month}, рік: {year}')
    # Пройдемося по регіонам
    for region in region_code:
        # url = f'https://openbudget.gov.ua/api/localBudgets/{bud_type}/?codeBudget={region[1]}&fundType={fund}&treeType=WITHOUT_DETALISATION&year={year}&periodType=MONTH&periodTo={month}&periodFrom={month}'
        url = f'https://openbudget.gov.ua/api/localBudgets/{bud_type}/?codeBudget={region[1]}&fundType={fund}&treeType=undefined&year={year}&periodType=MONTH&periodTo={month}&periodFrom={month}'
        # Завантаження JSON-файлу
        data = pd.read_json(url)
        # Розгортання підкатегорій у всіх рівнях вкладеності
        flat_data = []
        for item in data['items']:
            flat_data.extend(flatten_categories(item))

        # Створення DataFrame з розгорнутими даними
        output_data = pd.DataFrame(flat_data)
        # Додамо стовбчик з роком
        output_data['year'] = year
        # Додамо стовбчик з місяцем
        output_data['month'] = month
        # Додамо стовбчик з регіоном
        output_data['region_name'] = region[0]
        # Додамо кодом регіону
        output_data['region_code'] = region[1]
        # Додамо стовбчик з першим днем місяця
        output_data['date_start'] = pd.to_datetime(f'{year}-{month}-01')
        # Додамо стовбчик з останнім днем місяця
        output_data['date_end'] = pd.to_datetime(f'{year}-{month}-01') + MonthEnd(1)
        # Додамо до загального DataFrame
        df_result = df_result.append(output_data)
        # Затримка від 1 до 3 секунд
        time.sleep(random.randint(1, 3))

# В датафреймі df4 залишимо лише ті рядки, де в стовбчику "Level" значення 4
df4 = df_result[df_result['Level'] == 4]
# В датафреймі df4 залишимо лише ті рядки, де в стовбчику "Code" є значення зі списку categories
df4 = df4[df4['Code'].isin(categories)]
# В датафреймі df_result залишимо лише ті рядки, де в стовбчику "Level" значення не 4
df_result = df_result[df_result['Level'] != 4]
# В стовбчику "Code 3" вставимо знасення з стовбчика "Code" (замінивши останні 4 символи на "0000")
df4['Code 3'] = df4['Code'].apply(lambda x: re.sub(r'\d{4}$', '0000', x))
# В стовбчику "Code 2" вставимо знасення з стовбчика "Code" (замінивши останні 6 символів на "000000")
df4['Code 2'] = df4['Code'].apply(lambda x: re.sub(r'\d{6}$', '000000', x))
# В стовбчику "Code 1" вставимо знасення з стовбчика "Code" (замінивши останні 7 символів на "0000000")
df4['Code 1'] = df4['Code'].apply(lambda x: re.sub(r'\d{7}$', '0000000', x))
# В стовбчику "Code Name 3" вставимо значення зі стовбчика "Code Name" датафрейму df_result, якщо  співпадають значення в стовбчиках "date_start" а також співпадає значення з стовбчика "Code 3" (df4) і "Code" (df_result)
df4['Code Name 3'] = df4.apply(lambda x: df_result[(df_result['date_start'] == x['date_start']) & (df_result['Code'] == x['Code 3'])]['Code Name'].values[0], axis=1)
# В стовбчику "Code Name 2" вставимо значення зі стовбчика "Code Name" датафрейму df_result, якщо  співпадають значення в стовбчиках "date_start" а також співпадає значення з стовбчика "Code 2" (df4) і "Code" (df_result)
df4['Code Name 2'] = df4.apply(lambda x: df_result[(df_result['date_start'] == x['date_start']) & (df_result['Code'] == x['Code 2'])]['Code Name'].values[0], axis=1)
# В стовбчику "Code Name 1" вставимо значення зі стовбчика "Code Name" датафрейму df_result, якщо  співпадають значення в стовбчиках "date_start" а також співпадає значення з стовбчика "Code 1" (df4) і "Code" (df_result)
df4['Code Name 1'] = df4.apply(lambda x: df_result[(df_result['date_start'] == x['date_start']) & (df_result['Code'] == x['Code 1'])]['Code Name'].values[0], axis=1)

# Збережемо сторбці в такій послідовності date_start Code Code Name Code 1 Code Name 1 Code 2 Code Name 2 Code 3 Code Name 3 DonePeriod CorrectionYearDonePercent
df4 = df4[['date_start', 'date_end', 'month', 'region_name', 'Code 1', 'Code Name 1', 'Code 2', 'Code Name 2', 'Code 3',
           'Code Name 3', 'Code', 'Code Name', 'RozpisZmin', 'DonePeriod', 'CorrectionYearDonePercent']]
# Збережемо в форматі Excel
df4.to_excel('output.xlsx', index=False)

# Перекладемо df4 на англійську мову використовуючи словник dict_en
df4 = myReplace(df4, dict_en)
df4.to_excel('output_en.xlsx', index=False)
