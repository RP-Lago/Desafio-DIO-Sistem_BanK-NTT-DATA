Aqui está a versão melhorada e mais atraente do seu texto do README.md:

---

## Sistema Bancário Orientado a Objetos em Python

Este projeto desenvolve um **sistema bancário completo em Python**, utilizando os princípios de **Programação Orientada a Objetos (POO)**, como classes, herança, encapsulamento e polimorfismo. Ele permite criar clientes (pessoas físicas), contas bancárias e realizar operações fundamentais como depósitos, saques e consultas de extrato.

### Baseado no Desafio da DIO

Esta solução foi inspirada no desafio de código da [Digital Innovation One (DIO)](https://www.dio.me/), orientado pelo especialista [Guilherme Carvalho](https://www.linkedin.com/in/decarvalhogui). O desafio original utilizava dicionários para armazenamento de dados, mas nesta versão, as informações são estruturadas em objetos, alinhados ao **modelo UML de classes**.

### Diagrama UML - Visão das Classes

![Diagrama UML](diagrama_classes.png)

### Funcionalidades Principais

- **Cadastro de Clientes**: Crie novos clientes, fornecendo nome, data de nascimento, CPF e endereço (buscado automaticamente via **API ViaCEP**).
- **Abertura de Contas**: Crie contas bancárias associadas a clientes (atualmente, apenas Conta Corrente).
- **Depósitos**: Realize depósitos em contas existentes.
- **Saques**: Realize saques, respeitando os limites de saldo, saque e quantidade de operações diárias.
- **Extrato Bancário**: Consulte o histórico completo de transações e saldo atual.
- **Listagem de Contas**: Veja todas as contas bancárias cadastradas.
- **Persistência de Dados**: Os dados de clientes e contas são salvos automaticamente em um arquivo JSON (`banco_de_dados.json`), permitindo continuidade entre sessões do programa.

### Destaques e Inovações

- **Decorator para Log de Transações**: Utilização de `@log_transaction` para registrar transações de forma automática e organizada.
- **Tratamento Robusto de Erros**: Mecanismos de validação para entradas inválidas, falhas na API ViaCEP e problemas de leitura/escrita no arquivo JSON.
- **Testes Unitários**: Testes básicos foram implementados para garantir a qualidade da classe `ContaCorrente`.

### Como Executar

1. **Instale as Dependências**: Certifique-se de que a biblioteca `requests` está instalada. Utilize o comando:
   ```bash
   pip install requests
   ```
2. **Execute o Programa**: Rode o arquivo Python principal com o comando:
   ```bash
   python seu_codigo.py
   ```

### Próximos Passos

- **Novos Tipos de Conta**: Planeja-se adicionar tipos como Conta Poupança e Conta Salário.
- **Transferências Bancárias**: Implementar transferências entre contas.
- **Interface Gráfica**: Tornar o sistema mais amigável através de uma interface gráfica.
- **Segurança**: Adicionar autenticação de usuário e outras medidas de segurança.

### Contribuições

Sinta-se à vontade para contribuir! Sugestões, pull requests e novas funcionalidades são sempre bem-vindas.

---

**Observações**:
- O diagrama UML foi criado usando [PlantUML](https://plantuml.com/).
- O Diagrama UML pode ser gerado com a extensão [PlantUML](https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml) 
- Lembre-se de substituir o arquivo `SistemaBankDiagram.png` pelo caminho correto do seu diagrama UML.

---

Esse novo formato realça suas implementações, destacando o uso de boas práticas e recursos avançados como decoradores, além de torná-lo mais acessível e profissional.