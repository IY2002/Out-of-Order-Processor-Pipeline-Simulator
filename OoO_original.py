import sys

# various global variables for different things (explained later)
instruction_list = []
cycle_counter = 0
instruction_counter = 0
writeback_queue = []
issue_queue = []
dispatch_queue = []
rename_queue = []
decode_queue = []
fetch_queue = []
commit_queue = []
pr2ar = {}
number_of_commited_instructions = 0
load_store_queue = {}
# to read the input text document


def read_input():
    file_name = sys.argv[1]
    doc = open(file_name, "r")
    global numPRegs
    global issueWidth
    numPRegs, issueWidth = doc.readline().split(",")
    numPRegs = int(numPRegs)
    issueWidth = int(issueWidth)

    # save the instructions into an array of lists
    global instruction_list
    counter = 0
    while True:
        line = doc.readline()
        if line == "":
            break
        instrType, r1, r2, r3 = line.split(",")
        r1 = int(r1)
        r2 = int(r2)
        r3 = int(r3)
        # number each instruction with a number for ease of mind later on
        instruction_list.append([counter, instrType, r1, r2, r3])
        counter += 1

    # generate the various tables and lists need to run the pipeline
    global mapTable
    global freeList
    global readyTable
    global load_store_queue
    # this variable is a dictionary to tell what each physical register maps to what architectural register
    global pr2ar
    mapTable = {}
    # register 0-31 are reserved for architecture
    freeList = [i for i in range(32, numPRegs)]
    # intially all the registers are ready since they are not in use
    readyTable = [True for _ in range(numPRegs)]
    # the first 32 registers amp to themselves obviously
    for i in range(32):
        mapTable[i] = [i]
        pr2ar[i] = i
        load_store_queue[i] = []

    doc.close()


def fetch():
    global fetch_queue
    global decode_queue
    global issueWidth
    global load_store_queue
    counter = 0
    # while there are instructions to get and theres room in my pipeline
    while (counter < issueWidth and len(instruction_queue) != 0):
        # add the first instruction to the pipeline
        current_instruction = instruction_queue.pop(0)
        if current_instruction[1] == 'L' or current_instruction[1] == 'S':
            load_store_queue[current_instruction[2]].append(
                current_instruction[0])
        # write what cycle this stage was executed
        output_list[current_instruction[0]].append(cycle_counter)

        # push instruction into next stage
        decode_queue.append(current_instruction)

        counter += 1


def decode():
    global decode_queue
    global rename_queue
    counter = 0
    while (counter < issueWidth and len(decode_queue) != 0):
        # execute current instruction in the pipeline
        current_instruction = decode_queue.pop(0)

        # write what cycle this was executed
        output_list[current_instruction[0]].append(cycle_counter)

        # push instruction to next stage
        rename_queue.append(current_instruction)

        counter += 1


def rename():
    global rename_queue
    global dispatch_queue
    counter = 0
    while (counter < issueWidth and len(rename_queue) != 0):
        # boolean to keep track if the instruction is executed or not
        executed_instruction = False
        # print(rename_queue)
        # get the next instruction to execute
        current_instruction = rename_queue.pop(0)

        # if there are no free registers then the dispatch cannot be executed for L, R and I instructions since the rename cant be done
        if len(freeList) > 0:

            if current_instruction[1] == 'L':
                # append to output cycle number
                output_list[current_instruction[0]].append(cycle_counter)

                # update instruction to have most up to date version of register
                current_instruction[4] = mapTable[pr2ar[current_instruction[4]]][-1]

                # get next avaible free register
                register = freeList.pop(0)

                # set to to not ready
                readyTable[register] = False

                # map it to its architecural register
                pr2ar[register] = pr2ar[current_instruction[2]]
                mapTable[pr2ar[current_instruction[2]]].append(register)

                # update instruction to have pyhsical register instead of architectural register
                current_instruction[2] = register

                # push instruction to next stage in pipeline
                dispatch_queue.append(current_instruction)

                # the instruction is executed
                executed_instruction = True

            if current_instruction[1] == 'I':
                # append to output cycle number
                output_list[current_instruction[0]].append(cycle_counter)

                # update instruction to have most up to date version of register
                current_instruction[3] = mapTable[pr2ar[current_instruction[3]]][-1]

                # get next avaible free register
                register = freeList.pop(0)

                # set to to not ready
                readyTable[register] = False

                # map it to its architecural register
                pr2ar[register] = pr2ar[current_instruction[2]]
                mapTable[pr2ar[current_instruction[2]]].append(register)

                # update instruction to have pyhsical register instead of architectural register
                current_instruction[2] = register

                # push instruction to next stage in pipeline
                dispatch_queue.append(current_instruction)

                # the instruction is executed
                executed_instruction = True

            if current_instruction[1] == 'R':
                # append to output cycle number
                output_list[current_instruction[0]].append(cycle_counter)

                # update instructions to have most up to date version of register
                current_instruction[3] = mapTable[pr2ar[current_instruction[3]]][-1]
                current_instruction[4] = mapTable[pr2ar[current_instruction[4]]][-1]

                # get next avaible free register
                register = freeList.pop(0)

                # set to to not ready
                readyTable[register] = False

                # map it to its architecural register
                pr2ar[register] = pr2ar[current_instruction[2]]
                mapTable[pr2ar[current_instruction[2]]].append(register)

                # update instruction to have pyhsical register instead of architectural register
                current_instruction[2] = register

                # push instruction to next stage in pipeline
                dispatch_queue.append(current_instruction)

                # the instruction is executed
                executed_instruction = True

        if current_instruction[1] == 'S':
            # update output with cycle instruction is executed
            output_list[current_instruction[0]].append(cycle_counter)

            # update instructions to have most up to date version of register
            current_instruction[2] = mapTable[pr2ar[current_instruction[2]]][-1]
            current_instruction[4] = mapTable[pr2ar[current_instruction[4]]][-1]

            # push instruction to next stage in pipeline
            dispatch_queue.append(current_instruction)
            # print(mapTable)
            # the instruction is executed
            executed_instruction = True

        # this means the instruction was not executed so it should be put back in the queue but in the front not the back
        if not executed_instruction:
            rename_queue.insert(0, current_instruction)

        counter += 1


def dispatch():
    global dispatch_queue
    global issue_queue
    counter = 0
    # print(dispatch_queue)

    while (counter < issueWidth and len(dispatch_queue) != 0):
        # print(dispatch_queue)

        # add the first instruction to the pipeline
        current_instruction = dispatch_queue.pop(0)

        # write what cycle this stage was executed
        output_list[current_instruction[0]].append(cycle_counter)
        # push instruction into next stage
        issue_queue.append(current_instruction)

        counter += 1


# helper function to decide what instruction should be issued next
def issue_helper():
    # go through list in reverse since priorty is given to older instructions
    for i in reversed(range(len(issue_queue))):
        instr = issue_queue[i]

        # L instructions need the memory destination register to be ready to be executed
        if instr[1] == 'L':
            if readyTable[instr[4]] == True:
                issue_queue.pop(i)
                return instr

        # R-type instructions need both registers to be ready to be executed
        elif instr[1] == 'R':
            if readyTable[instr[3]] == True and readyTable[instr[4]] == True:
                issue_queue.pop(i)
                return instr

        # S instructions need both the data and memory location ready to be executed
        elif instr[1] == 'S':
            if readyTable[instr[2]] == True and readyTable[instr[4]] == True:
                issue_queue.pop(i)
                return instr

        # I-type instructions need the source register to be ready to be executed
        elif instr[1] == 'I':
            if readyTable[instr[3]] == True:
                issue_queue.pop(i)
                return instr

    # if there are no instructions in the queue that are ready then return -1
    return -1


def issue():
    global issue_queue
    global writeback_queue
    counter = 0
    issue_queue.sort(key=lambda x: int(x[0]))
    while counter < issueWidth and len(issue_queue) != 0:
        # find instruction to be ran next using helper function
        current_instruction = issue_helper()

        # if an instruction is found ready to be executed
        if current_instruction != -1:
            # append cycle counter to instruction
            output_list[current_instruction[0]].append(cycle_counter)
            # print(current_instruction)
            # print(readyTable)
            # print(pr2ar)
            # push instruction to next cycle
            writeback_queue.append(current_instruction)

        counter += 1

# need to do the stalling for consecutive loads and stores from the same register

# CREATE A LOAD STORE QUEUE THAT IS A DICTIONARY WITH EACH REGISTER AS THE KEYS AND THE VALUES ARE
# THE ORDER IN WHICH THE INSTRUCTIONS SHOULD BE COMMITED USING THE INATRUCTION NUMBER  TO IDENTITFY WIHCH ONE


def writeback():
    global writeback_queue
    global commit_queue
    counter = 0
    archeticural_registers_being_loaded_or_stored = []

    while (counter < issueWidth and len(writeback_queue) != 0):
        # get isntruction to execute
        current_instruction = writeback_queue.pop(0)
        # if it is a store or load instruction then need to check the load_store_queue to see if its turn to be loaded or stored
        if current_instruction[1] == 'S' or current_instruction[1] == 'L':
            if current_instruction[0] == load_store_queue[pr2ar[current_instruction[2]]][0] and pr2ar[current_instruction[2]] not in archeticural_registers_being_loaded_or_stored:
                # Need to do the loads and stores
                output_list[current_instruction[0]].append(cycle_counter)
                archeticural_registers_being_loaded_or_stored.append(
                    pr2ar[current_instruction[2]])
                load_store_queue[pr2ar[current_instruction[2]]].pop(0)
            else:
                writeback_queue.insert(0, current_instruction)
        else:
            output_list[current_instruction[0]].append(cycle_counter)

        # if there is something to write back, then it has been written and the register value is ready
        if current_instruction[1] == 'R' or current_instruction[1] == 'I' or current_instruction[1] == 'L':
            readyTable[current_instruction[2]] = True

        # push instruction to next stage
        commit_queue.append(current_instruction)
        counter += 1


# keep track of what instruction should be committed next since it is in order
next_instruct_to_be_committed = 0
registers_to_free = []


def commit():
    global commit_queue
    global next_instruct_to_be_committed
    global number_of_commited_instructions
    counter = 0
    # registers are freed the cycle after the commit so this is me delaying the freeing of the registers
    for register in registers_to_free:
        freeList.insert(0, register)
    while (counter < issueWidth and len(commit_queue) != 0):
        # execute instruction in pipeline in order so sort the commit queue by instruction number
        commit_queue.sort(key=lambda x: int(x[0]))

        # commit is in order so this checks the number of the first instruction in the commit queue after its sorted to see if its the right one
        if commit_queue[0][0] == next_instruct_to_be_committed:
            # the correc tcomit instruction is found so it should be popped
            current_instruction = commit_queue.pop(0)
            # if current_instruction[1] == 'R':
            #     readyTable[current_instruction[2]] = True
            # if there was a register from the freelist used it will be added back to the freelist in the next cycle
            # using the registers to free list which is emptied at the begining of each commit
            if current_instruction[1] == 'R' or current_instruction[1] == 'I' or current_instruction[1] == 'L':
                registers_to_free.append(current_instruction[2])
                mapTable[pr2ar[current_instruction[2]]].remove(
                    current_instruction[2])
            output_list[current_instruction[0]].append(cycle_counter)

            # next comit is for the next instruction in order
            next_instruct_to_be_committed += 1
            number_of_commited_instructions += 1
        counter += 1


def create_output_file():
    with open('out.txt', 'w') as f:
        # Write the output text to the file
        for i in output_list:
            f.write(str(i[0]) + ',' + str(i[1]) + ',' + str(i[2]) + ',' +
                    str(i[3]) + ',' + str(i[4]) + ',' + str(i[5]) + ',' + str(i[6]) + '\n')
        f.close()


def main():
    read_input()
    global instruction_list
    global instruction_queue
    global cycle_counter
    global output_list
    instruction_count = len(instruction_list)
    instruction_queue = instruction_list
    output_list = [[] for _ in range(instruction_count)]
    counter = 0
    while number_of_commited_instructions != instruction_count:
        commit()
        writeback()
        issue()
        dispatch()
        rename()
        decode()
        fetch()
        cycle_counter += 1
    create_output_file()


if __name__ == "__main__":
    main()
