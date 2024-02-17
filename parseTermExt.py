import xml.etree.ElementTree as ET

#Funcion para pasar el numero de terminal de 002 -> 2
def clearNumber(number):
    if number[0]=='0':
        number = number[1] + number[2]
        if number[0]=='0':
            number = number[1]
    return int(number)

#Funcion para pasar el numero de terminal de 2 -> 002
def prettierNumber(number):
    number = str(number)
    if len(number)==1:
        number ='00' + number
    elif len(number)==2:
        number = '0' + number
    else:
        number = number
    return number

#Funcion para construir los rangos denuevo. Eg. 001,002,003 -> 001-003
def buildRanges(terminalRange):
    #Dividimos la cadena en una lista de números y conviértelos en enteros
    terminals = [int(term) for term in terminalRange.split(',')]

    #Ordenamos los números de menor a mayor
    terminals = sorted(terminals)

    ranges = []
    start = end = terminals[0] 

    for term in terminals[1:]:
        if term == end + 1:
            end = term
        else:
            if start == end:
                ranges.append(str(prettierNumber(start)))
            else:
                ranges.append(f"{prettierNumber(start)}-{prettierNumber(end)}")
            start = end = term

    # Agrega el último rango
    if start == end:
        ranges.append(str(prettierNumber(start)))
    else:
        ranges.append(f"{prettierNumber(start)}-{prettierNumber(end)}")

    #Juntamos todos los rangos separados por comas
    terminalRange_final = ','.join(ranges)

    #Retornamos la cadena final
    return terminalRange_final

#Clase Terminal donde se guarda el rango y las extensiones que contiene
class Terminal(object):
    def __init__(self, rango):
        self.rango = rango
        self.extensions = list()
        self.oldLigado = None
        self.newLigado = None

    #Metodo para imprimir el objeto
    def __str__(self):
        cad = f"\n{self.rango} | oldLigado:{self.oldLigado} newLigado:{self.newLigado}"
        for ext in self.extensions:
            cad+=f"\n{ext.suffix} + {ext.location}"
        return cad

#Clase extensiones donde se guardan los atributos suffix y location
class Extension(object):
    def __init__(self, suffix, location):
        self.suffix = suffix
        self.location = location 

#Clase Load donde se guarda el rango y el contenido de esta
class Load(object):
    def __init__(self, rango, contenido):
        self.rango = rango
        self.oldLigado = None
        self.newLigado = None
        self.contenido = contenido

    #Metodo para imprimir el objeto
    def __str__(self):
        cad = f"\n{self.rango} | oldLigado:{self.oldLigado} | newLigado:{self.newLigado} | Contenido:{self.contenido}"
        return cad
    
    #Metodo para parsear las LoadDefinitions
    def parseTerm(self):
        if len(self.rango)>0:
            rango = f'<TerminalLoadDefinition terminalRange="{buildRanges(self.rango)}">\n'
            rango += "".join(self.contenido)
            return rango
        else:
            return ''

## - ADXXTSDK.DAT (Docker)
## - ADXXTSJP.DAT (Embedded JavaPOS)
## - ADXXTSGT.DAT (GTK)
## - ADXXTSFF.DAT (Mozilla based Web Mbrowser)
## - ADXXTSPG.DAT (PostgreSQL)
## - ADXXTSNO.DAT (Netop)
## - ADXXTSRT.DAT (RXTX)
## - ADXXTSJ8.DAT (TDK8)
## - ADXXTSSH.DAT (SSH)

terminalsToAdd = '001-020,022-040,042-060'
extensionsToAdd = "ADXXTSDK.DAT,ADXXTSFF.DAT,ADXXTSSH.DAT"
locationDefault = "adx_spgm:"

#Borramos los espacios en el string de extensiones
extensionsToAdd = extensionsToAdd.replace(' ','')
#Las dividimos por comas en una lista
extensionsToAdd = extensionsToAdd.split(',')
#Borramos los espacios en el string de terminales
terminalsToAdd = terminalsToAdd.replace(' ','')
#Las dividimos por comas en una lista
terminalsToAdd = terminalsToAdd.split(',')
#Lista para almacenar las terminales de tipo rango temporalmente
rangesFound = list()
#Lista para almacenar las terminales individuales temporalmente
normalsFound = list()
#Lista para juntar las terminales de ambos tipos al final
finalNews = list()

#Vamos a recorrer cada elemento de las terminales nuevas
for terminal in terminalsToAdd:
    #Si encuentra un - es de tipo rango. Eg. xxx-xxx
    if(terminal.find('-')!=-1):
        #Partimos el rango para identificar el rango menor y el rango mayor
        tempRanges = terminal.split('-')
        lower_term = tempRanges[0]
        higher_term = tempRanges[1]
        #Si los rangos estan en orden correcto. Eg. rangoMenor-rangoMayor
        if lower_term < higher_term:
            #Ingreamos cada terminal a la lista. Eg. 001-003 -> Se ingresan 001,002,003
            for x in range(int(lower_term), int(higher_term) + 1):
                finalNews.append(str(prettierNumber(x)))
        #Si los rangos estan alreves. Eg. rangoMayor-rangoMenor
        elif lower_term > higher_term:
            #Simplemente los intercambiamos y los ingresamos a la lista
            temp = lower_term
            lower_term = higher_term
            higher_term = temp
            for x in range(int(lower_term), int(higher_term) + 1):
                finalNews.append(str(prettierNumber(x)))
    #Si no, es de tipo individual y solo la metemos a la lista           
    else:
        finalNews.append(terminal)

#Limpiamos los ceros para poder sortear la lista. Eg. 001 -> 1
terminalsToAdd = list(map(clearNumber, finalNews))
#Ordenamos la lista de mayor a menor
terminalsToAdd.sort()
#Con la lista ya ordenada volvemos a ponerle los ceros a las terminals. Eg. 1 -> 001
terminalsToAdd = list(map(prettierNumber, terminalsToAdd))

#Parseamos el XML
tree = ET.parse('TERMEXT.XML')
root = tree.getroot()

#Lo abrimos, lo leemos y guardamos el contenido en la variable text
with open(('TERMEXT.XML'), 'r', encoding='utf-8') as f:
    text = f.read()

#Usando slicing guardamos en la variable header todo el header
header = text[:text.find('<LoadDefinitionExtension terminalRange='):]

#Creamos la lista de x de 0 a 999
existingTerminals = list()
for x in range(0,999):
    existingTerminals.append('x')  

#Creamos una lista para guardar las terminales existentes
temp_existingTerminals = list()

#Indice para asociar las terminales existentes a su terminalRange
indexTerminalRange = 0
#root contiene todo el texto del xml, con el for recorremos cada etiqueta que coincida con LoadDefinitionExtension
for bcapp in root.findall('LoadDefinitionExtension'):
    #De cada LoadDefinitionExtension extraemos el contenido de su atributo terminalRange y lo convertimos a string
    name = str(bcapp.get('terminalRange'))
    #Separamos cada terminal en una lista
    name = name.split(',')
    #Vamos a recorrer cada terminal
    for term in name:
        #Si la terminal contiene - es de tipo rango
        if term.find('-')!= -1:
            #Dividimos el rango para identificar el rangoMayor y el rangoMenor
            tempRanges = term.split('-')
            lower_term = int(tempRanges[0])
            higher_term = int(tempRanges[1])
            #Vamos a recorrer el rango y vamos a crear un objeto tipo Terminal por cada terminal existente
            #Eg. 001-003 -> Se crea un objeto con 001,002,003
            for r in range(lower_term,higher_term + 1):
                terminal = Terminal(prettierNumber(r))
                #A todas las terminales de un mismo terminalRange se les pone el mismo numero de oldLigado para que
                #se identifiquen como de la misma terminalRange
                terminal.oldLigado = indexTerminalRange
                for ccapp in bcapp.find('Extensions'):
                    suffix = str(ccapp.get('suffix'))
                    location = str(ccapp.get('location'))
                    #Creamos un objeto Extension con los valores extraidos
                    extension = Extension(suffix,location)
                    #Y dicho objeto lo asociamos a la terminal metiendolo al atributo extensiones(que es una lista) del objeto Terminal
                    terminal.extensions.append(extension)
                temp_existingTerminals.append(terminal)
        #Si es de tipo individual
        else:
            #Simplemente creamos su objeto y lo metemos a la lista de existentes temporal
            terminal = Terminal(term)
            terminal.oldLigado = indexTerminalRange
            for ccapp in bcapp.find('Extensions'):
                suffix = str(ccapp.get('suffix'))
                location = str(ccapp.get('location'))
                #Creamos un objeto Extension con los valores extraidos
                extension = Extension(suffix,location)
                #Y dicho objeto lo asociamos a la terminal metiendolo al atributo extensiones(que es una lista) del objeto Terminal
                terminal.extensions.append(extension)
            temp_existingTerminals.append(terminal)
    #Aumentamos el indice para para que cada terminalRange tenga uno diferente
    indexTerminalRange += 1

#Ingresamos las terminales existentes a su respectivo indice de la lista existingTerminals. Eg. Terminal 001 se pone en el 
#indice 1 de la lista existingTerminals
for term in temp_existingTerminals:
    indice = int(clearNumber(term.rango))
    for x in range(len(existingTerminals)):
        if x == indice:
            existingTerminals[x] = term

evaluationStarted = False
#Lista que guarda las extensiones que tiene un terminalRange que se usa más adelantes
existingExtensions = list()
#Lista para guardar las terminales nuevas que no se encuentran en las existentes
terminalsFullNew = list()
#Lista que contendra las extensiones que no esten repetidas y se tengan que meter a la terminal existente
addedExtensions = list()
#Flag para saber cuando por lo menos una nueva extension no esta dentro de las existentes en la terminal
positive = False
#Indice que tendran en la lista modified
newIndexTerminalRange = 0
#Lista para meter las terminales existentes modificadas
modifiedTerminals = list()

#Vamos a buscar que las terminales nuevas existan en existingTerminals como indices. Eg. Terminal nueva igual a 001,
#buscaremos si existe un objeto en el indice 1
for n in terminalsToAdd:
    existingExtensions.clear()
    addedExtensions.clear()
    numTerm = int(n)
    #Si el indice no tiene una 'x' quiere decir que hay un objeto guardado y por lo tanto la terminal nueva existe dentro
    #de las existentes
    if existingTerminals[numTerm] != 'x':         
        #Sacamos las extensiones de la existente 
        for ex in existingTerminals[numTerm].extensions:
            existingExtensions.append(ex.suffix)
        #Si la extraccion se hizo correctamente
        if existingExtensions:
            #Vamos a buscar si las nuevas extensiones no estan ya dentro de las existente
            for exNew in extensionsToAdd:
                if exNew not in existingExtensions:
                    positive = True
                    addedExtensions.append(exNew) 

            #Si por lo menos una no esta dentro comenzamos el proceso     
            if positive:
                #Creamos un objeto extension por cada extension nueva que no este ya dentro de la terminal
                #y la metemos a sus extensiones
                for exNew in addedExtensions:
                    suffix = exNew
                    location = locationDefault
                    extension = Extension(suffix,location)
                    existingTerminals[numTerm].extensions.append(extension)
                
                #Aqui vamos a comenzar a separar las terminales que no fueron modificadas y las que si
                #y a su vez las vamos a mantener ligadas para despues juntarlas en sus respectivos
                #terminalRange, el primer if solo se usa una vez, al comienzo
                if evaluationStarted == False:
                    #Asignamos el numero inicial que ligará a las terminales modificadas
                    existingTerminals[numTerm].newLigado = newIndexTerminalRange
                    #Guardamos temporalmente el numero que ligaba a la terminal en su antiguo terminalRange
                    temp_oldLigado = existingTerminals[numTerm].oldLigado
                    #Borramos el numero del antiguo ligado(esto no es tan necesario)
                    existingTerminals[numTerm].oldLigado = None
                    #Lo metemos a la lista de terminales modificadas
                    modifiedTerminals.append(existingTerminals[numTerm])
                    #Reemplazamos el objeto en la lista antigua con una equis
                    existingTerminals[numTerm] = 'x'
                    evaluationStarted = True
                else:
                    #Si el numero que ligación antiguo de la terminal que se esta analizando en el momento
                    #es igual al de la terminal anterior quiere decir que pertenecian al mismo terminalRange,
                    #eso quiere decir que tienen las mismas extensiones
                    if existingTerminals[numTerm].oldLigado == temp_oldLigado:
                        #Por lo que se les asigna el mismo numero de ligación para la nueva lista
                        existingTerminals[numTerm].newLigado = newIndexTerminalRange
                        temp_oldLigado = existingTerminals[numTerm].oldLigado
                        existingTerminals[numTerm].oldLigado = None
                        modifiedTerminals.append(existingTerminals[numTerm])
                        existingTerminals[numTerm] = 'x'
                    #En cambio si son diferentes quiere decir que la terminal actual pertenece a otro terminalRange
                    elif existingTerminals[numTerm].oldLigado != temp_oldLigado:
                        #Por lo que se aumenta el numero de ligación de la nueva lista y se le asigna
                        newIndexTerminalRange += 1
                        existingTerminals[numTerm].newLigado = newIndexTerminalRange
                        temp_oldLigado = existingTerminals[numTerm].oldLigado
                        existingTerminals[numTerm].oldLigado = None
                        modifiedTerminals.append(existingTerminals[numTerm])
                        existingTerminals[numTerm] = 'x'
            #Si ya estan todas no hacemos nada
            else:
                pass
    #Si el indice tiene una 'x' quiere decir que no habia una terminal existente con el mismo numero que la nueva,
    #por lo que es una completamente nueva
    else:     
        #Creamos el objeto con sus extensiones
        terminal = Terminal(prettierNumber(numTerm))
        for exNew in extensionsToAdd:
            suffix = exNew
            location = locationDefault
            extension = Extension(suffix,location)
            terminal.extensions.append(extension)
        #La metemos a la lista de terminales completamente nuevas
        terminalsFullNew.append(terminal)


#--------- Juntando denuevo las terminales existentes que no se modificaron ---------#

#Borramos las equis de la lista existingTerminals y las ponemos en la lista clean_existingTerminals
clean_existingTerminals = [term for term in existingTerminals if not term == 'x']
final_existingList = list()   

#linkedNumber contiene inicialmente el numero oldLigado del primer objeto terminal
linkedNumber = clean_existingTerminals[0].oldLigado
exten = list()
tempRange = list()
concatenatedRange = list()
terminalRangeChanged = False

#exten contendra inicialmente las extensiones del primer objeto terminal
for ex in clean_existingTerminals[0].extensions:
    exten.append(ex.suffix)

#Comenzamos el proceso para juntar denuevo las terminales que pertenecian al mismo terminalRange
for index, term in enumerate(clean_existingTerminals):
    #No se entra a este if hasta que se comience a evaluar una terminal que pertenezca a otro terminalRange
    #que el inicial
    if terminalRangeChanged == True:
        #Si entramos se limpia exten que es la lista que usamos para guardar las extensiones del terminalRange
        exten.clear()
        for ex in term.extensions:
            exten.append(ex.suffix)
        #Volvemos a cambiar la flag para que este lista cuando el script cominece a evaluar otro terminalRange
        terminalRangeChanged = False

    #Si el oldligado que es el valor que relaciona a las terminales por estar en el mismo terminal range, es igual
    #a linkedNumber, quiere decir que pertenecen al mismo terminalRange
    if term.oldLigado == linkedNumber:
        #Se comprueba que no estemos evaluando el ultimo elemento, ya que por la el funcionamiento del algoritmo
        #el ultimo elemento no alcanzaria a evaluarse, en dado caso que si se el ultimo se hace lo siguiente:
        if index == len(clean_existingTerminals) - 1:
            #Ingresamos la ultima terminal a la lista tempral
            tempRange.append(term.rango) 
            #Concatenamos todas las terminales usando comas para crear el terminalRange
            concatenatedRange.append(",".join(tempRange))
            #Creamos el objeto terminal con el rango que construimos
            terminal = Terminal(concatenatedRange[0])
            #Metemos sus extensiones
            for ex in exten:
                suffix = ex
                location = locationDefault
                #Creamos un objeto Extension con los valores extraidos
                extension = Extension(suffix,location)
                #Y dicho objeto lo asociamos a la terminal metiendolo al atributo extensiones(que es una lista) del objeto Terminal
                terminal.extensions.append(extension)
            final_existingList.append(terminal)
        #Si no estamos evaluando el ultimo elemento simplemente lo metemos a la lista temporal tempRange que es donde vamos
        #guardamos las terminales que pertenecen al mismo terminalRange
        else:
            tempRange.append(term.rango)

    #Si term.oldLigado no es igual a linkedNumber        
    else:
        #Si es el ultimo elemento de la lista que estamos evaluando, significaria que el ultimo terminalRange
        #solo tiene un elemento o realmente es el ultimo
        if index == len(clean_existingTerminals) - 1:
            #Concatenamos con comas para crear el terminalRange de las terminales que veniamos acumulando
            concatenatedRange.append(",".join(tempRange))
            #Creamos el objeto Terminal
            terminal = Terminal(concatenatedRange[0])
            #Metemos sus extensiones
            for ex in exten:
                suffix = ex
                location = locationDefault
                #Creamos un objeto Extension con los valores extraidos
                extension = Extension(suffix,location)
                #Y dicho objeto lo asociamos a la terminal metiendolo al atributo extensiones(que es una lista) del objeto Terminal
                terminal.extensions.append(extension)
            #Ingresamos el objeto a la lista final de terminales existentes
            final_existingList.append(terminal)

            #Limpiamos las listas que ocupamos
            concatenatedRange.clear()
            tempRange.clear()
            #Ingresamos a la lista acumulativa el ultimo elemento de la lista
            tempRange.append(term.rango)
            #Concatenamos con comas
            concatenatedRange.append(",".join(tempRange))
            #Limpiamos exten porque vamos a meter en ella las extensiones de la ultima terminal
            exten.clear()
            for ex in term.extensions:
                exten.append(ex.suffix)
            #Creamos el objeto
            terminal = Terminal(concatenatedRange[0])
            #Creamos y le asignamos sus extensiones
            for ex in exten:
                suffix = ex
                location = locationDefault
                #Creamos un objeto Extension con los valores extraidos
                extension = Extension(suffix,location)
                #Y dicho objeto lo asociamos a la terminal metiendolo al atributo extensiones(que es una lista) del objeto Terminal
                terminal.extensions.append(extension)
            #Metemos el objeto a la lista final
            final_existingList.append(terminal)
        
        #En dado caso que no sea el ultimo elemento a evaluar, eso significa que estamos cambiando de terminalRange
        #y este contiene 2 o más elementos
        else:
            #Concatenamos las terminales que veniamos acumulando
            concatenatedRange.append(",".join(tempRange))
            #Creamos el objeto
            terminal = Terminal(concatenatedRange[0])
            #Ingresamos sus extensiones
            for ex in exten:
                suffix = ex
                location = locationDefault
                #Creamos un objeto Extension con los valores extraidos
                extension = Extension(suffix,location)
                #Y dicho objeto lo asociamos a la terminal metiendolo al atributo extensiones(que es una lista) del objeto Terminal
                terminal.extensions.append(extension)
            #Metemos el objeto a la lista final
            final_existingList.append(terminal)

            #Limpiamos las listas que necesitamos ya que se va a evaluar un nuevo terminalRange
            concatenatedRange.clear()
            tempRange.clear()
            #Metemos la terminal actual a la lista acumulativa que es donde se detectó un cambio de terminalRange
            tempRange.append(term.rango)
            #Cambiamos el linkedNumber al nuevo term.oldLigado para que evalue las terminales del nuevo
            #terminalRange
            linkedNumber = term.oldLigado
            #Cambiamos esta flag para que se ejecute lo del principio del for
            terminalRangeChanged = True
          

#--------- Juntando denuevo las terminales existentes que se modificaron ---------#
####En esta parte, el funcionamiento es el mismo que el anterior script, solo que este se hace
####para las terminales que si fueron modificadas y separadas de los rangos originales

final_modifiedList = list()   

linkedNumber = modifiedTerminals[0].newLigado
exten.clear()
tempRange.clear()
concatenatedRange.clear()
terminalRangeChanged = False

for ex in modifiedTerminals[0].extensions:
    exten.append(ex.suffix)

for index, term in enumerate(modifiedTerminals):
    if terminalRangeChanged == True:
        exten.clear()
        for ex in term.extensions:
            exten.append(ex.suffix)
        terminalRangeChanged = False

    if term.newLigado == linkedNumber:
        if index == len(modifiedTerminals) - 1:
            tempRange.append(term.rango) 
            concatenatedRange.append(",".join(tempRange))
            terminal = Terminal(concatenatedRange[0])
            for ex in exten:
                suffix = ex
                location = locationDefault
                extension = Extension(suffix,location)
                terminal.extensions.append(extension)
            final_modifiedList.append(terminal)
        else:
            tempRange.append(term.rango)
    else:
        if index == len(modifiedTerminals) - 1:
            concatenatedRange.append(",".join(tempRange))
            terminal = Terminal(concatenatedRange[0])
            for ex in exten:
                suffix = ex
                location = locationDefault
                extension = Extension(suffix,location)
                terminal.extensions.append(extension)
            final_modifiedList.append(terminal)

            concatenatedRange.clear()
            tempRange.clear()
            tempRange.append(term.rango)
            concatenatedRange.append(",".join(tempRange))
            exten.clear()
            for ex in term.extensions:
                exten.append(ex.suffix)
            terminal = Terminal(concatenatedRange[0])
            for ex in exten:
                suffix = ex
                location = locationDefault
                extension = Extension(suffix,location)
                terminal.extensions.append(extension)
            final_modifiedList.append(terminal)
        else:
            concatenatedRange.append(",".join(tempRange))
            terminal = Terminal(concatenatedRange[0])
            for ex in exten:
                suffix = ex
                location = locationDefault
                extension = Extension(suffix,location)
                terminal.extensions.append(extension)
            final_modifiedList.append(terminal)

            concatenatedRange.clear()
            tempRange.clear()
            tempRange.append(term.rango)
            linkedNumber = term.newLigado
            terminalRangeChanged = True           


#--------- Juntando las terminales que son totalmente nuevas ---------#

final_newTerminalsList = list()

#Limpiamos las listas para reutilizarlas
exten.clear()
tempRange.clear()
concatenatedRange.clear()

#Si existe contenido dentro de la lista que contiene las terminales nuevas entra
if len(terminalsFullNew) != 0:
    #Como son nuevas, todas las terminales contendran las mismas extensiones asi que tomamos como referencia las del primer 
    #objeto y las metemos a la lista exten
    for ex in terminalsFullNew[0].extensions:
        exten.append(ex.suffix)

    #Metemos los rangos de las nuevas a una lista tempRange
    for term in terminalsFullNew:
        tempRange.append(term.rango)

    #Concatenamos los elementos de tempRange en una string llamado concatenatedRange
    concatenatedRange.append(','.join(tempRange))
    #Creamos el objeto terminal
    terminal = Terminal(concatenatedRange[0])
    #Y agregamos sus extensiones que guardamos en exten
    for ex in exten:
        suffix = ex
        location = locationDefault
        #Creamos un objeto Extension con los valores extraidos
        extension = Extension(suffix,location)
        #Y dicho objeto lo asociamos a la terminal metiendolo al atributo extensiones(que es una lista) del objeto Terminal
        terminal.extensions.append(extension)
    #Finalmente las metemos a la lista final de terminales completamente nuevas.
    final_newTerminalsList.append(terminal)

#Metemos el header del xml inicial a una variable llamada xml  
xml = header

#Ingresamos las terminales existentes que terminaron modificadas
for terminal in final_existingList:
    #Antes de imprimir el rango, lo enviamos a una funcion que las ordena y vuelve a crear los rangos. Eg. 001,002,003 -> 001-003
    rango = buildRanges(terminal.rango)
    xml+=f'<LoadDefinitionExtension terminalRange="{rango}">\n<Extensions>\n'
    for extension in terminal.extensions:
        xml+=f'<Extension suffix="{extension.suffix}" location="{extension.location}"/>\n'
    xml+='</Extensions>\n</LoadDefinitionExtension>\n'

#Ingresamos las terminales que se extrageron de los rangos existentes
for terminal in final_modifiedList:
    #Antes de imprimir el rango, lo enviamos a una funcion que las ordena y vuelve a crear los rangos. Eg. 001,002,003 -> 001-003
    rango = buildRanges(terminal.rango)
    xml+=f'<LoadDefinitionExtension terminalRange="{rango}">\n<Extensions>\n'
    for extension in terminal.extensions:
        xml+=f'<Extension suffix="{extension.suffix}" location="{extension.location}"/>\n'
    xml+='</Extensions>\n</LoadDefinitionExtension>\n'

#Verificamos si hay elementos en la lista primero
if len(final_newTerminalsList) != 0:
    #Ingresamos las terminales completamente nuevas que no estaban en las existentes
    for terminal in final_newTerminalsList:
        #Antes de imprimir el rango, lo enviamos a una funcion que las ordena y vuelve a crear los rangos. Eg. 001,002,003 -> 001-003
        rango = buildRanges(terminal.rango)
        xml+=f'<LoadDefinitionExtension terminalRange="{rango}">\n<Extensions>\n'
        for extension in terminal.extensions:
            xml+=f'<Extension suffix="{extension.suffix}" location="{extension.location}"/>\n'
        xml+='</Extensions>\n</LoadDefinitionExtension>\n'    

footer = '</LoadDefinitionExtensionFile>'
xml+=footer

#Escribimos el file
with open('NEWTERMEXT.XML', 'w') as output:
    output.write(xml)


###################################################################
###################################################################
#-------- Modificando los rangos de las Load Definitions ---------#
###################################################################
###################################################################

#Lo abrimos, lo leemos y guardamos el contenido en la variable text
with open(('LOADDEF.XML'), 'r', encoding='utf-8') as f:
    text = f.read()

#Usando slicing guardamos en la variable header todo el header
header = text[:text.find('<TerminalLoadDefinition terminalRange='):]

with open("LOADDEF.XML", "r") as f:
    text = f.readlines()

#Sacamos contenido de cada objeto de load
termExist = list()
for line in text:
    if(line.find('<TerminalLoadDefinition terminalRange')!=-1):
        for x in range(text.index(line), len(text)):
            if text[x].find('</TerminalLoadDefinition>')!=-1:
                termExist.append(text[text.index(line):x+1])
                break

#Guardamos el contenido en una lista para usarlo despues 
terminalsContent = list()
for term in termExist:
    terminalContent = term[1:len(term)]
    terminalsContent.append(terminalContent)  

#Parseamos el XML
tree = ET.parse('LOADDEF.XML')
root = tree.getroot()

temp_existingTerminals.clear()
#Indice para asociar las terminales existentes a su terminalRange
indexTerminalRange = 0

#root contiene todo el texto del xml, con el for recorremos cada etiqueta que coincida con LoadDefinitionExtension
for bcapp in root.findall('TerminalLoadDefinition'):
    #De cada LoadDefinitionExtension extraemos el contenido de su atributo terminalRange y lo convertimos a string
    name = str(bcapp.get('terminalRange'))
    #Separamos cada terminal en una lista
    name = name.split(',')
    #Vamos a recorrer cada terminal
    for term in name:
        #Si la terminal contiene - es de tipo rango
        if term.find('-')!= -1:
            #Dividimos el rango para identificar el rangoMayor y el rangoMenor
            tempRanges = term.split('-')
            lower_term = int(tempRanges[0])
            higher_term = int(tempRanges[1])
            #Vamos a recorrer el rango y vamos a crear un objeto tipo Terminal por cada terminal existente
            #Eg. 001-003 -> Se crea un objeto con 001,002,003
            for r in range(lower_term,higher_term + 1):
                terminalsContent[indexTerminalRange]
                terminal = Load(prettierNumber(r), terminalsContent[indexTerminalRange])
                #A todas las terminales de un mismo terminalRange se les pone el mismo numero de oldLigado para que
                #se identifiquen como de la misma terminalRange
                terminal.oldLigado = indexTerminalRange
                temp_existingTerminals.append(terminal)
        #Si es de tipo individual
        else:
            #Simplemente creamos su objeto y lo metemos a la lista de existentes temporal
            terminal = Load(term, terminalsContent[indexTerminalRange])
            terminal.oldLigado = indexTerminalRange
            temp_existingTerminals.append(terminal)
    #Aumentamos el indice para para que cada terminalRange tenga uno diferente
    indexTerminalRange += 1

existingTerminals.clear()

#Creamos la lista de x de 0 a 999
for x in range(0,999):
    existingTerminals.append('x')

#Ingresamos las terminales existentes a su respectivo indice de la lista existingTerminals. Eg. Terminal 001 se pone en el 
#indice 1 de la lista existingTerminals
for term in temp_existingTerminals:
    indice = int(clearNumber(term.rango))
    for x in range(len(existingTerminals)):
        if x == indice:
            existingTerminals[x] = term

#Flag para saber que por lo menos se ejecuto una vez la evaluación
evaluationStarted = False
#Indice que tendran en la lista modified
newIndexTerminalRange = 0
#Lista para meter las terminales existentes modificadas
modifiedTerminals.clear()
#Lista para guardar las terminales nuevas que no se encuentran en las existentes
terminalsFullNew.clear()

#Vamos a buscar que las terminales nuevas existan en existingTerminals como indices. Eg. Terminal nueva igual a 001,
#buscaremos si existe un objeto en el indice 1
for n in terminalsToAdd:
    numTerm = int(n)
    #Si el indice no tiene una 'x' quiere decir que hay un objeto guardado y por lo tanto la terminal nueva existe dentro
    #de las existentes
    if existingTerminals[numTerm] != 'x':                
        #Aqui vamos a comenzar a separar las terminales que no fueron modificadas y las que si
        #y a su vez las vamos a mantener ligadas para despues juntarlas en sus respectivos
        #terminalRange, el primer if solo se usa una vez, al comienzo
        if evaluationStarted == False:
            #Asignamos el numero inicial que ligará a las terminales modificadas
            existingTerminals[numTerm].newLigado = newIndexTerminalRange
            #Guardamos temporalmente el numero que ligaba a la terminal en su antiguo terminalRange
            temp_oldLigado = existingTerminals[numTerm].oldLigado
            #Borramos el numero del antiguo ligado(esto no es tan necesario)
            existingTerminals[numTerm].oldLigado = None
            #Lo metemos a la lista de terminales modificadas
            modifiedTerminals.append(existingTerminals[numTerm])
            #Reemplazamos el objeto en la lista antigua con una equis
            existingTerminals[numTerm] = 'x'
            evaluationStarted = True
        else:
            #Si el numero que ligación antiguo de la terminal que se esta analizando en el momento
            #es igual al de la terminal anterior quiere decir que pertenecian al mismo terminalRange,
            #eso quiere decir que tienen las mismas extensiones
            if existingTerminals[numTerm].oldLigado == temp_oldLigado:
            #Por lo que se les asigna el mismo numero de ligación para la nueva lista
                existingTerminals[numTerm].newLigado = newIndexTerminalRange
                temp_oldLigado = existingTerminals[numTerm].oldLigado
                existingTerminals[numTerm].oldLigado = None
                modifiedTerminals.append(existingTerminals[numTerm])
                existingTerminals[numTerm] = 'x'
                #En cambio si son diferentes quiere decir que la terminal actual pertenece a otro terminalRange
            elif existingTerminals[numTerm].oldLigado != temp_oldLigado:
                #Por lo que se aumenta el numero de ligación de la nueva lista y se le asigna
                newIndexTerminalRange += 1
                existingTerminals[numTerm].newLigado = newIndexTerminalRange
                temp_oldLigado = existingTerminals[numTerm].oldLigado
                existingTerminals[numTerm].oldLigado = None
                modifiedTerminals.append(existingTerminals[numTerm])
                existingTerminals[numTerm] = 'x'
    #Si el indice tiene una 'x' quiere decir que no habia una terminal existente con el mismo numero que la nueva,
    #por lo que es una completamente nueva
    else:     
        pass

#--------- Juntando denuevo las terminales existentes que no se modificaron ---------#

#Borramos las equis de la lista existingTerminals y las ponemos en la lista clean_existingTerminals
clean_existingTerminals.clear()
final_existingList.clear()  

clean_existingTerminals = [term for term in existingTerminals if not term == 'x']

#linkedNumber contiene inicialmente el numero oldLigado del primer objeto terminal con el que se iniciara la evaluacion
linkedNumber = clean_existingTerminals[0].oldLigado
tempRange.clear()
concatenatedRange.clear()
terminalRangeChanged = False

#loadContent contendra inicialmente el contenido del primer objeto terminal
loadContent = clean_existingTerminals[0].contenido

#Comenzamos el proceso para juntar denuevo las terminales que pertenecian al mismo terminalRange
for index, term in enumerate(clean_existingTerminals):
    
    #Si el oldligado que es el valor que relaciona a las terminales por estar en el mismo terminal range, es igual
    #a linkedNumber, quiere decir que pertenecen al mismo terminalRange 
    if term.oldLigado == linkedNumber:
        #Se comprueba que no estemos evaluando el ultimo elemento, ya que por la el funcionamiento del algoritmo
        #el ultimo elemento no alcanzaria a evaluarse, en dado caso que si se el ultimo se hace lo siguiente:
        if index == len(clean_existingTerminals) - 1:
             #Ingresamos la ultima terminal a la lista tempral
            tempRange.append(term.rango) 
            #Concatenamos todas las terminales usando comas para crear el terminalRange
            concatenatedRange.append(",".join(tempRange))
            #Creamos el objeto load con el rango que construimos
            terminal = Load(concatenatedRange[0], loadContent)
            final_existingList.append(terminal)
        #Si no estamos evaluando el ultimo elemento simplemente lo metemos a la lista temporal tempRange que es donde vamos
        #guardamos las terminales que pertenecen al mismo terminalRange
        else:
            tempRange.append(term.rango)
    
    #Si term.oldLigado no es igual a linkedNumber        
    else:
        #Si es el ultimo elemento de la lista que estamos evaluando, significaria que el ultimo terminalRange
        #solo tiene un elemento o realmente es el ultimo
        if index == len(clean_existingTerminals) - 1:
            #Concatenamos con comas para crear el terminalRange de las terminales que veniamos acumulando
            concatenatedRange.append(",".join(tempRange))
            #Creamos el objeto Load
            terminal = Load(concatenatedRange[0],loadContent)
            #Ingresamos el objeto a la lista final de terminales existentes
            final_existingList.append(terminal)

            #Limpiamos las listas que ocupamos
            concatenatedRange.clear()
            tempRange.clear()
            #Ingresamos a la lista acumulativa el ultimo elemento de la lista
            tempRange.append(term.rango)
            #Concatenamos con comas
            concatenatedRange.append(",".join(tempRange))
            #Actualizamos el contenido de la load anterior
            loadContent = term.contenido
            #Creamos el objeto
            terminal = Load(concatenatedRange[0],loadContent)
            #Metemos el objeto a la lista final
            final_existingList.append(terminal)
        else:
            #Concatenamos con comas
            concatenatedRange.append(",".join(tempRange))
            #Creamos el objeto de la terminal evaluado en la iteracion anterior
            terminal = Load(concatenatedRange[0],loadContent)
            #Metemos el objeto a la lista final
            final_existingList.append(terminal)
            #Limpiamos las listas que necesitamos ya que se va a evaluar un nuevo terminalRange
            concatenatedRange.clear()
            tempRange.clear()
            #Metemos la terminal en curso a la lista acumualtiva
            tempRange.append(term.rango)
            #Actualizamos el contenido por el de la terminal evaluandose
            loadContent = term.contenido
            #Cambiamos el linkedNumber al nuevo term.oldLigado para que evalue las terminales del nuevo
            #terminalRange
            linkedNumber = term.oldLigado    

#--------- Juntando denuevo las terminales existentes que se modificaron ---------#
####En esta parte, el funcionamiento es el mismo que el anterior script, solo que este se hace
####para las terminales que si fueron modificadas y separadas de los rangos originales

final_modifiedList = list()   

linkedNumber = modifiedTerminals[0].newLigado
tempRange.clear()
concatenatedRange.clear()
terminalRangeChanged = False

loadContent = modifiedTerminals[0].contenido

for index, term in enumerate(modifiedTerminals):
    
    if term.newLigado == linkedNumber:
        if index == len(modifiedTerminals) - 1:
            tempRange.append(term.rango) 
            concatenatedRange.append(",".join(tempRange))
            terminal = Load(concatenatedRange[0], loadContent)
            final_modifiedList.append(terminal)
        else:
            tempRange.append(term.rango)
            
    else:
        if index == len(modifiedTerminals) - 1:
            concatenatedRange.append(",".join(tempRange))
            terminal = Load(concatenatedRange[0],loadContent)
            final_modifiedList.append(terminal)

            concatenatedRange.clear()
            tempRange.clear()
            tempRange.append(term.rango)
            concatenatedRange.append(",".join(tempRange))
            loadContent = term.contenido
            terminal = Load(concatenatedRange[0],loadContent)
            final_modifiedList.append(terminal)
        else:
            concatenatedRange.append(",".join(tempRange))
            terminal = Load(concatenatedRange[0],loadContent)
            final_modifiedList.append(terminal)
            concatenatedRange.clear()
            tempRange.clear()
            tempRange.append(term.rango)
            loadContent = term.contenido
            linkedNumber = term.newLigado
            terminalRangeChanged = True

#Metemos el header del xml inicial a una variable llamada xml  
xml = ""
xml = xml + header

for term in final_existingList:
    xml = xml + term.parseTerm()

for term in final_modifiedList:
    xml = xml + term.parseTerm()    
    
footer = '</TerminalLoadDefinitionFile>'
xml+=footer

#Escribimos el file
with open('NEWLOADDEF.XML', 'w') as output:
    output.write(xml)