    function setSignals(){
            IPython.notebook.kernel.execute(`
                ALUOut_value = ALUOut.read(0)
                branch_value = branch.read(0)
                print(f"ALUOut:{ALUOut_value},branch:{branch_value}")
            `, {
                iopub: {
                    output: data => {
                        console.log(data)
                        let output = data.content.text.trim().split(",")
                        output.forEach(output => {
                            output  = output.split(":")
                            const element = document.getElementById(output[0])
                            const value = parseInt(output[1], 10)
                            if (element.tagName === "INPUT") {
                                element.value = "0x" + value.toString(16)
                            } else if (element.tagName === ("BUTTON")){
                                element.textContent = value === 1 ? '1' : '0';
                                element.classList.remove('mod-success', 'mod-danger');
                                element.classList.add(value === 1 ? 'mod-success' : 'mod-danger');  
                            }
                        })
                    }
                }
            });
        }