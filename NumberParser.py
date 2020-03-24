

class numericParser():
    """
    Class to parse string in english international system to numeric
    attributes:
        input: number_in_string
        output: parsed_string

    Example:
            obj = numericParser("seven hundred and sixty-five thousand, four hundred and thirty-two")
            print(obj.parsed_number) #765432
         
    """"
    numbers = dict()
    numbers["one"] = 1
    numbers["two"] = 2
    numbers["three"] = 3
    numbers["four"] = 4
    numbers["five"] = 5
    numbers["six"] = 6
    numbers["seven"] = 7
    numbers["eight"] = 8
    numbers["nine"] = 9
    numbers["ten"] = 10
    numbers["eleven"] = 11
    numbers["twelve"] = 12
    numbers["thirteen"] = 13
    numbers["fourteen"] = 14
    numbers["fifteen"] = 15
    numbers["sixteen"] = 16
    numbers["seventeen"] = 17
    numbers["eighteen"] = 18
    numbers["nineteen"] = 19
    numbers["twenty"] = 20
    numbers["thirty"] = 30
    numbers["fourty"] = 40; numbers["forty"] = 40
    numbers["fifty"] = 50
    numbers["sixty"] = 60
    numbers["seventy"] = 70
    numbers["eighty"] = 80
    numbers["ninety"] = 90
    numbers["hundred"] = 10**2
    numbers["thousand"] = 10**3
    numbers["million"] = 10**6
    numbers["billion"] = 10**9
    decimal_system_powers = ["billion", "million", "thousand", "hundred"] 
    
    def __init__(self, number_in_string):
        """ 
        
        """
        self.number_in_string = number_in_string
        self.parsed_number = self.parse()
    def cleaned_string(self, string):
        
        string = string.replace(" and ", " ") # spaces around 'and' are important
        string = string.replace(",", " ")
        string = string.replace("-", " ")
        return string
    
    def string_as_list(self, string):
        return list(map(lambda x:x.strip(), string.split()))

    def parse(self):
        string_chunks = self.string_as_list(
            self.cleaned_string(self.number_in_string))

        self.parsed_number = 0
        indices_big_powers = [-1]
        for i in self.decimal_system_powers:
            try:
                index = string_chunks.index(i, indices_big_powers[-1] + 1)
                indices_big_powers.append(index)
            except ValueError:
                continue
            except:
                raise "UNIDENTIFIED ERROR"
        else:
            indices_big_powers.append(len(string_chunks))    
    

        i = 0
        while i< len(indices_big_powers) - 1:
            initial, final = indices_big_powers[i: i+2]
            initial, final = initial + 1, final
            temp = 0
            for j in range(initial, final):
                if string_chunks[j] in self.decimal_system_powers:
                    temp *= self.numbers[string_chunks[j]]
                else:    
                    temp += self.numbers[string_chunks[j]]

            if final < len(string_chunks):
                temp *= self.numbers[string_chunks[final]]
            self.parsed_number += temp
            i += 1
        return self.parsed_number

if __name__ == "__main__":
    obj = numericParser("seven hundred and sixty-five thousand, four hundred and thirty-two")
    print(obj.parsed_number)
