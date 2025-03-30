from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.list import MDList, OneLineIconListItem
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.utils import platform
import json
import os
import uuid

# Configuração para melhor visualização em dispositivos móveis
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

class DrawerList(MDList):
    pass

class ContentNavigationDrawer(ScrollView):
    pass

class TelaLogin(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.criar_layout()
        
    def criar_layout(self):
        box_layout = MDBoxLayout(
            orientation="vertical", 
            spacing=dp(10), 
            padding=dp(20),
            adaptive_height=False
        )
        
        # Título
        titulo = MDLabel(
            text="Transporte Escolar",
            halign="center",
            font_style="H4",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(80)
        )
        
        subtitulo = MDLabel(
            text="Crie uma conta ou selecione uma existente",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(50)
        )
        
        # Botões
        botao_criar = MDRaisedButton(
            text="CRIAR NOVA CONTA",
            size_hint=(1, None),
            height=dp(50),
            elevation=3,
            on_release=self.app.mostrar_dialog_criar_conta
        )
        
        botao_selecionar = MDRaisedButton(
            text="SELECIONAR CONTA EXISTENTE",
            size_hint=(1, None),
            height=dp(50),
            elevation=3,
            md_bg_color=self.app.theme_cls.accent_color,
            on_release=self.app.mostrar_dialog_selecionar_conta
        )
        
        # Adicionar widgets
        box_layout.add_widget(titulo)
        box_layout.add_widget(subtitulo)
        box_layout.add_widget(MDBoxLayout(size_hint_y=None, height=dp(30)))  # Espaço
        box_layout.add_widget(botao_criar)
        box_layout.add_widget(MDBoxLayout(size_hint_y=None, height=dp(20)))  # Espaço
        box_layout.add_widget(botao_selecionar)
        
        self.add_widget(box_layout)

class TelaInfoEstudante(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.criar_layout()
        
    def criar_layout(self):
        box_layout = MDBoxLayout(
            orientation="vertical", 
            spacing=dp(15), 
            padding=dp(20),
            adaptive_height=False
        )
        
        # Título
        titulo = MDLabel(
            text="Informações do Estudante",
            halign="center",
            font_style="H5",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(60)
        )
        
        # Campos para nome e turma
        self.nome_field = MDTextField(
            hint_text="Nome do Aluno",
            required=True,
            helper_text="Obrigatório",
            helper_text_mode="on_error",
            size_hint_y=None,
            height=dp(60)
        )
        
        self.turma_field = MDTextField(
            hint_text="Turma",
            required=True,
            helper_text="Obrigatório",
            helper_text_mode="on_error",
            size_hint_y=None,
            height=dp(60)
        )
        
        # Botão de continuar
        botao_continuar = MDRaisedButton(
            text="CONTINUAR",
            size_hint=(1, None),
            height=dp(50),
            elevation=3,
            on_release=self.continuar
        )
        
        # Adicionar widgets
        box_layout.add_widget(titulo)
        box_layout.add_widget(MDBoxLayout(size_hint_y=None, height=dp(20)))  # Espaço
        box_layout.add_widget(self.nome_field)
        box_layout.add_widget(self.turma_field)
        box_layout.add_widget(MDBoxLayout(size_hint_y=None, height=dp(40)))  # Espaço
        box_layout.add_widget(botao_continuar)
        
        self.add_widget(box_layout)
    
    def continuar(self, *args):
        nome = self.nome_field.text
        turma = self.turma_field.text
        
        if not nome or not turma:
            self.app.mostrar_info_dialog("Por favor, preencha todos os campos obrigatórios.")
            return
        
        # Salvar informações do estudante na conta atual
        self.app.conta_atual["nome_aluno"] = nome
        self.app.conta_atual["turma"] = turma
        self.app.salvar_contas()
        
        # Ir para a tela principal
        self.app.screen_manager.current = "principal"

class TransporteApp(MDApp):
    dialog = None
    estudantes = []
    contas = []
    conta_atual = None
    arquivo_dados = 'estudantes.json'
    arquivo_contas = 'contas.json'
    
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Light"
        
        # Carregar dados existentes
        self.carregar_dados()
        self.carregar_contas()
        
        # Criar gerenciador de telas
        self.screen_manager = ScreenManager()
        
        # Adicionar tela de login
        self.tela_login = TelaLogin(app=self, name="login")
        self.screen_manager.add_widget(self.tela_login)
        
        # Adicionar tela de informações do estudante
        self.tela_info_estudante = TelaInfoEstudante(app=self, name="info_estudante")
        self.screen_manager.add_widget(self.tela_info_estudante)
        
        # Adicionar tela principal
        self.tela_principal = MDScreen(name="principal")
        self.criar_tela_principal()
        self.screen_manager.add_widget(self.tela_principal)
        
        # Definir tela inicial
        if self.contas:
            self.screen_manager.current = "login"
        else:
            self.screen_manager.current = "login"
        
        return self.screen_manager
    
    def carregar_contas(self):
        try:
            if os.path.exists(self.arquivo_contas):
                with open(self.arquivo_contas, 'r') as arquivo:
                    self.contas = json.load(arquivo)
            else:
                # Lista de alunos pré-cadastrados
                alunos = [
                    {"nome": "Giovanna", "nome_aluno": "Giovanna Andrade Rodrigues Porto", "turma": "3A"},
                    {"nome": "Kallil", "nome_aluno": "Kallil Henrique Félix dos Santos Pereira", "turma": "3A"},
                    {"nome": "Maria Eduarda", "nome_aluno": "Maria Eduarda Farias Cavalcante", "turma": "3A"},
                    {"nome": "Hugo", "nome_aluno": "Hugo Carvalho Silva", "turma": "3A"},
                    {"nome": "Nathasha", "nome_aluno": "Nathasha Teixeira Carvalho Furtado", "turma": "3A"},
                    {"nome": "Saskia", "nome_aluno": "Saskia Beatriz Teodoro Carvalho", "turma": "3A"},
                    {"nome": "Iasmim", "nome_aluno": "Iasmim Francisca Santana de Carvalho", "turma": "3A"},
                    {"nome": "Isabelle", "nome_aluno": "Isabelle Silva Santos", "turma": "3A"},
                    {"nome": "Michele", "nome_aluno": "Michele Keila Sousa e Souza", "turma": "3A"},
                    {"nome": "Guilherme", "nome_aluno": "Guilherme Luíz Conradi", "turma": "3A"},
                    {"nome": "Nathan", "nome_aluno": "Nathan Pyerre Alves Lima De Sousa", "turma": "3A"},
                    {"nome": "José Wilson", "nome_aluno": "José Wilson Soares de Araújo Neto", "turma": "3A"},
                    {"nome": "Sophia", "nome_aluno": "Sophia Waleska Azevedo de Oliveira", "turma": "3A"},
                    {"nome": "Maisa", "nome_aluno": "Maisa Eduarda da Silva Neves", "turma": "3A"},
                    {"nome": "Ana Carolina", "nome_aluno": "Ana Carolina Silva", "turma": "3A"},
                    {"nome": "Arielle", "nome_aluno": "Arielle Lorranny Lira dos Santos", "turma": "3A"},
                    {"nome": "Sthella", "nome_aluno": "Sthella Nascimento de Almeida", "turma": "3A"},
                    {"nome": "Rafaela", "nome_aluno": "Rafaela Silva Santos", "turma": "3A"},
                    {"nome": "Heitor", "nome_aluno": "Heitor Carvalho Mateus", "turma": "3A"},
                    {"nome": "Keihysson", "nome_aluno": "Keihysson Freitas Oliveira", "turma": "3A"},
                    {"nome": "Eduarda", "nome_aluno": "Eduarda Da Silva Gomes", "turma": "3A"},
                    {"nome": "Ana Vitória", "nome_aluno": "Ana Vitória Vieira Dantas", "turma": "3A"},
                    {"nome": "Giulia", "nome_aluno": "Giulia Almeida Reis", "turma": "3A"},
                    {"nome": "Camillo", "nome_aluno": "Camillo Gomes Viana", "turma": "3A"},
                    {"nome": "Anna Laura", "nome_aluno": "Anna Laura Costa Matos", "turma": "3A"},
                    {"nome": "Ana Maria", "nome_aluno": "Ana Maria Souza Mageveski", "turma": "3A"},
                    {"nome": "Francielson", "nome_aluno": "Francielson Figueiredo Araújo da Silva", "turma": "3A"},
                    {"nome": "Daniel", "nome_aluno": "Daniel Pereira Gomes", "turma": "3A"},
                    {"nome": "Jessica", "nome_aluno": "Jessica Maira Neves Fontoura", "turma": "3A"},
                    {"nome": "Kemyle", "nome_aluno": "Kemyle de Araújo Nascimento", "turma": "3A"},
                    {"nome": "Ana Livia", "nome_aluno": "Ana Livia Carvalho Neves", "turma": "3A"},
                    {"nome": "Henrique", "nome_aluno": "Henrique de Carvalho Nunes", "turma": "3A"},
                    {"nome": "Ayslanna", "nome_aluno": "Ayslanna Eduarda Tavares Costa", "turma": "3A"},
                    {"nome": "Heloá", "nome_aluno": "Heloá Jheniffer Sousa Silva", "turma": "3A"},
                    {"nome": "Júlio", "nome_aluno": "Júlio Keven da Silva Nascimento Correia", "turma": "3A"},
                    {"nome": "Bárbara", "nome_aluno": "Bárbara Silva Schmid", "turma": "3A"},
                    {"nome": "Matheus", "nome_aluno": "Matheus dos Santos Nascimento", "turma": "3A"},
                    {"nome": "Ana Alice", "nome_aluno": "Ana Alice Araújo", "turma": "3A"},
                    {"nome": "Geraldo", "nome_aluno": "Geraldo Kairo Teixeira da Silva", "turma": "3A"},
                    {"nome": "João Gabriel", "nome_aluno": "João Gabriel de Brito Macedo", "turma": "3A"},
                    {"nome": "Anna Beatriz", "nome_aluno": "Anna Beatriz Moura Marroques de Oliveira", "turma": "3A"},
                    {"nome": "Valdery", "nome_aluno": "Valdery Andrews Ferreira da Silva", "turma": "3A"}
                ]

                self.contas = []
                for aluno in alunos:
                    self.contas.append({
                        "id": str(uuid.uuid4()),
                        "nome": aluno["nome"],
                        "nome_aluno": aluno["nome_aluno"],
                        "turma": aluno["turma"],
                        "manha_ida": True,
                        "meiodia_ida": False,
                        "meiodia_volta": False,
                        "tarde_volta": True
                    })
                
                self.salvar_contas()
        except Exception as e:
            print(f"Erro ao carregar contas: {e}")
            self.contas = []

    # ... (restante dos métodos permanece exatamente igual ao código original)
    
    def criar_tela_principal(self):
        # Toolbar principal
        self.toolbar = MDTopAppBar(
            title="Transporte Escolar",
            elevation=10,
            pos_hint={"top": 1}
        )
        self.toolbar.left_action_items = [["menu", lambda x: self.nav_drawer.set_state("open")]]
        self.toolbar.right_action_items = [["account-switch", lambda x: self.voltar_para_login()]]
        
        # Navigation Drawer
        self.nav_drawer = MDNavigationDrawer(
            radius=(0, 16, 16, 0),
        )
        
        # Conteúdo do Navigation Drawer
        content_drawer = ContentNavigationDrawer()
        
        drawer_list = DrawerList()
        
        items = [
            {"text": "Mudar Horários", "icon": "clock-edit", "on_release": self.mostrar_dialog_adicionar},
            {"text": "Lista Manhã (Ida)", "icon": "bus-school", "on_release": lambda x: self.mostrar_lista("manha_ida")},
            {"text": "Lista Meio-dia (Ida)", "icon": "bus-school", "on_release": lambda x: self.mostrar_lista("meiodia_ida")},
            {"text": "Lista Meio-dia (Volta)", "icon": "bus-school", "on_release": lambda x: self.mostrar_lista("meiodia_volta")},
            {"text": "Lista 18:30 (Volta)", "icon": "bus-school", "on_release": lambda x: self.mostrar_lista("tarde_volta")},
            {"text": "Todos os Alunos", "icon": "account-group", "on_release": lambda x: self.mostrar_lista("todos")},
            {"text": "Trocar de Conta", "icon": "account-switch", "on_release": lambda x: self.voltar_para_login()}
        ]
        
        for item in items:
            drawer_item = OneLineIconListItem(text=item["text"], on_release=item["on_release"])
            drawer_list.add_widget(drawer_item)
        
        content_drawer.add_widget(drawer_list)
        self.nav_drawer.add_widget(content_drawer)
        
        # Layout principal
        self.main_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(10)
        )
        
        # Área de conteúdo principal (ScrollView)
        self.scroll_view = ScrollView()
        self.content_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(10),
            adaptive_height=True
        )
        
        # Mensagem inicial
        welcome_card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(8),
            size_hint=(1, None),
            height=dp(200),
            elevation=2,
            radius=[10]
        )
        
        welcome_title = MDLabel(
            text="Bem-vindo ao Sistema de Transporte Escolar",
            theme_text_color="Primary",
            font_style="H5",
            size_hint_y=None,
            height=dp(40)
        )
        
        welcome_text = MDLabel(
            text="Use o menu para visualizar as diferentes listas de transporte ou alterar seus horários.",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(100)
        )
        
        welcome_card.add_widget(welcome_title)
        welcome_card.add_widget(welcome_text)
        self.content_layout.add_widget(welcome_card)
        
        self.scroll_view.add_widget(self.content_layout)
        
        # Adicionando widgets ao layout principal
        self.main_layout.add_widget(self.toolbar)
        self.main_layout.add_widget(self.scroll_view)
        
        # Adicionando componentes à tela principal
        self.tela_principal.add_widget(self.main_layout)
        self.tela_principal.add_widget(self.nav_drawer)
    
    def voltar_para_login(self, *args):
        self.screen_manager.current = "login"
    
    def mostrar_dialog_criar_conta(self, *args):
        self.dialog_conta = MDDialog(
            title="Criar Conta - Digite seu nome",
            type="custom",
            content_cls=MDBoxLayout(
                orientation="vertical",
                spacing=dp(10),
                padding=dp(20),
                size_hint_y=None,
                height=dp(100),
                children=[
                    MDTextField(
                        id="nome_conta",
                        hint_text="Seu nome completo",
                        required=True,
                        helper_text="Obrigatório",
                        helper_text_mode="on_error"
                    )
                ]
            ),
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.dialog_conta.dismiss()
                ),
                MDRaisedButton(
                    text="CRIAR",
                    on_release=self.criar_conta
                )
            ]
        )
        self.dialog_conta.open()
    
    def criar_conta(self, *args):
        nome_conta = self.dialog_conta.content_cls.children[0].text
        if not nome_conta:
            return
        
        nova_conta = {
            "id": str(uuid.uuid4()),
            "nome": nome_conta,
            "nome_aluno": "",
            "turma": "",
            "manha_ida": False,
            "meiodia_ida": False,
            "meiodia_volta": False,
            "tarde_volta": False
        }
        
        self.contas.append(nova_conta)
        self.conta_atual = nova_conta
        self.salvar_contas()
        self.dialog_conta.dismiss()
        
        # Ir para tela de informações do estudante
        self.screen_manager.current = "info_estudante"
    
    def mostrar_dialog_selecionar_conta(self, *args):
        if not self.contas:
            self.mostrar_info_dialog("Não há contas criadas. Por favor, crie uma conta primeiro.")
            return
        
        box_contas = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            size_hint_y=None,
            height=dp(50 + len(self.contas) * 50)
        )
        
        for conta in self.contas:
            conta_btn = MDRaisedButton(
                text=f"{conta['nome']} - {conta.get('nome_aluno', 'Sem aluno')}",
                size_hint=(1, None),
                height=dp(40),
                on_release=lambda x, c=conta: self.selecionar_conta(c)
            )
            box_contas.add_widget(conta_btn)
        
        self.dialog_selecionar = MDDialog(
            title="Selecionar Conta",
            type="custom",
            content_cls=box_contas,
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.dialog_selecionar.dismiss()
                )
            ]
        )
        self.dialog_selecionar.open()
    
    def selecionar_conta(self, conta):
        self.conta_atual = conta
        self.dialog_selecionar.dismiss()
        
        # Se não tiver informações do aluno, ir para tela de informações
        if not conta.get('nome_aluno') or not conta.get('turma'):
            self.screen_manager.current = "info_estudante"
        else:
            self.screen_manager.current = "principal"
            self.atualizar_info_tela_principal()
    
    def atualizar_info_tela_principal(self):
        # Atualiza o título da toolbar com o nome do aluno
        if self.conta_atual and self.conta_atual.get('nome_aluno'):
            self.toolbar.title = f"Transporte - {self.conta_atual['nome_aluno']}"
    
    def mostrar_info_dialog(self, texto):
        self.info_dialog = MDDialog(
            title="Informação",
            text=texto,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.info_dialog.dismiss()
                )
            ]
        )
        self.info_dialog.open()
    
    def mostrar_dialog_adicionar(self, *args):
        if not self.conta_atual:
            self.mostrar_info_dialog("Por favor, selecione ou crie uma conta primeiro.")
            return
            
        if not self.dialog:
            self.dialog_content = MDBoxLayout(
                orientation="vertical",
                spacing=dp(10),
                padding=dp(20),
                size_hint_y=None,
                height=dp(300)
            )
            
            # Informações do aluno
            info_aluno = MDLabel(
                text=f"Aluno: {self.conta_atual.get('nome_aluno', '')}\nTurma: {self.conta_atual.get('turma', '')}",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(60)
            )
            
            # Opções de horários
            horarios_label = MDLabel(
                text="Selecione os horários:",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(30)
            )
            
            # Checkboxes para horários
            horarios_box = MDBoxLayout(
                orientation="vertical",
                spacing=dp(5),
                size_hint_y=None,
                height=dp(160)
            )
            
            # Ida de manhã
            manha_ida_box = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(30)
            )
            self.manha_ida_check = MDCheckbox(on_active=self.on_checkbox_active)
            self.manha_ida_check.group = "ida"
            self.manha_ida_check.active = self.conta_atual.get('manha_ida', False)
            manha_ida_label = MDLabel(
                text="Ida - Manhã",
                theme_text_color="Secondary"
            )
            manha_ida_box.add_widget(self.manha_ida_check)
            manha_ida_box.add_widget(manha_ida_label)
            
            # Ida ao meio-dia
            meiodia_ida_box = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(30)
            )
            self.meiodia_ida_check = MDCheckbox(on_active=self.on_checkbox_active)
            self.meiodia_ida_check.group = "ida"
            self.meiodia_ida_check.active = self.conta_atual.get('meiodia_ida', False)
            meiodia_ida_label = MDLabel(
                text="Ida - Meio-dia",
                theme_text_color="Secondary"
            )
            meiodia_ida_box.add_widget(self.meiodia_ida_check)
            meiodia_ida_box.add_widget(meiodia_ida_label)
            
            # Volta ao meio-dia
            meiodia_volta_box = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(30)
            )
            self.meiodia_volta_check = MDCheckbox(on_active=self.on_checkbox_active)
            self.meiodia_volta_check.group = "volta"
            self.meiodia_volta_check.active = self.conta_atual.get('meiodia_volta', False)
            meiodia_volta_label = MDLabel(
                text="Volta - Meio-dia",
                theme_text_color="Secondary"
            )
            meiodia_volta_box.add_widget(self.meiodia_volta_check)
            meiodia_volta_box.add_widget(meiodia_volta_label)
            
            # Volta à tarde
            tarde_volta_box = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(30)
            )
            self.tarde_volta_check = MDCheckbox(on_active=self.on_checkbox_active)
            self.tarde_volta_check.group = "volta"
            self.tarde_volta_check.active = self.conta_atual.get('tarde_volta', False)
            tarde_volta_label = MDLabel(
                text="Volta - 18:30",
                theme_text_color="Secondary"
            )
            tarde_volta_box.add_widget(self.tarde_volta_check)
            tarde_volta_box.add_widget(tarde_volta_label)
            
            # Adicionar checkboxes ao layout
            horarios_box.add_widget(manha_ida_box)
            horarios_box.add_widget(meiodia_ida_box)
            horarios_box.add_widget(meiodia_volta_box)
            horarios_box.add_widget(tarde_volta_box)
            
            # Adicionar todos os elementos ao diálogo
            self.dialog_content.add_widget(info_aluno)
            self.dialog_content.add_widget(horarios_label)
            self.dialog_content.add_widget(horarios_box)
            
            self.dialog = MDDialog(
                title="Alterar Horários",
                type="custom",
                content_cls=self.dialog_content,
                buttons=[
                    MDFlatButton(
                        text="CANCELAR",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.fechar_dialog
                    ),
                    MDRaisedButton(
                        text="SALVAR",
                        on_release=self.salvar_horarios
                    )
                ]
            )
        else:
            # Atualizar informações do aluno no diálogo
            children = self.dialog_content.children
            for child in children:
                if isinstance(child, MDLabel) and "Aluno:" in child.text:
                    child.text = f"Aluno: {self.conta_atual.get('nome_aluno', '')}\nTurma: {self.conta_atual.get('turma', '')}"
            
            # Atualizar checkbox status
            self.manha_ida_check.active = self.conta_atual.get('manha_ida', False)
            self.meiodia_ida_check.active = self.conta_atual.get('meiodia_ida', False)
            self.meiodia_volta_check.active = self.conta_atual.get('meiodia_volta', False)
            self.tarde_volta_check.active = self.conta_atual.get('tarde_volta', False)
            
        self.dialog.open()
    
    def on_checkbox_active(self, checkbox, value):
        # Se o checkbox do meio dia ida for marcado, marca automaticamente a volta às 18:30
        if checkbox == self.meiodia_ida_check and value:
            self.tarde_volta_check.active = True
            self.meiodia_volta_check.active = False
        
        # Se o checkbox da tarde volta for desmarcado e o meio dia ida estiver marcado,
        # reativa o checkbox da tarde volta
        elif checkbox == self.tarde_volta_check and not value and self.meiodia_ida_check.active:
            self.tarde_volta_check.active = True
    
    def fechar_dialog(self, *args):
        self.dialog.dismiss()
    
    def salvar_horarios(self, *args):
        if not self.conta_atual:
            self.mostrar_info_dialog("Por favor, selecione ou crie uma conta primeiro.")
            return
            
        # Verificar se pelo menos um horário de ida e um de volta foram selecionados
        if not (self.manha_ida_check.active or self.meiodia_ida_check.active):
            self.mostrar_info_dialog("Selecione pelo menos um horário de ida.")
            return
            
        if not (self.meiodia_volta_check.active or self.tarde_volta_check.active):
            self.mostrar_info_dialog("Selecione pelo menos um horário de volta.")
            return
        
        # Atualizar horários na conta atual
        self.conta_atual["manha_ida"] = self.manha_ida_check.active
        self.conta_atual["meiodia_ida"] = self.meiodia_ida_check.active
        self.conta_atual["meiodia_volta"] = self.meiodia_volta_check.active
        self.conta_atual["tarde_volta"] = self.tarde_volta_check.active
        
        # Atualizar a conta na lista de contas
        for i, conta in enumerate(self.contas):
            if conta["id"] == self.conta_atual["id"]:
                self.contas[i] = self.conta_atual
                break
        
        self.salvar_contas()
        self.fechar_dialog()
        self.mostrar_lista("todos")
    
    def mostrar_lista(self, tipo_lista):
        if not self.conta_atual:
            self.mostrar_info_dialog("Por favor, selecione ou crie uma conta primeiro.")
            return
            
        # Limpar conteúdo atual
        self.content_layout.clear_widgets()
        
        # Título da lista
        titulos = {
            "manha_ida": "Lista de Alunos - Manhã (Ida)",
            "meiodia_ida": "Lista de Alunos - Meio-dia (Ida)",
            "meiodia_volta": "Lista de Alunos - Meio-dia (Volta)",
            "tarde_volta": "Lista de Alunos - 18:30 (Volta)",
            "todos": "Lista de Todos os Alunos"
        }
        
        title_label = MDLabel(
            text=titulos.get(tipo_lista, "Lista de Alunos"),
            theme_text_color="Primary",
            font_style="H5",
            size_hint_y=None,
            height=dp(50)
        )
        self.content_layout.add_widget(title_label)
        
        # Conta atual
        conta_label = MDLabel(
            text=f"Conta: {self.conta_atual['nome']}",
            theme_text_color="Secondary",
            font_style="Body1",
            size_hint_y=None,
            height=dp(30)
        )
        self.content_layout.add_widget(conta_label)
        
        # Filtrar alunos por tipo de lista
        alunos = []
        for conta in self.contas:
            if tipo_lista == "todos" or conta.get(tipo_lista, False):
                # Só adiciona à lista se tiver nome e turma
                if conta.get('nome_aluno') and conta.get('turma'):
                    alunos.append(conta)
        
        # Exibir lista de alunos
        if not alunos:
            empty_label = MDLabel(
                text="Nenhum aluno cadastrado neste horário",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(50)
            )
            self.content_layout.add_widget(empty_label)
        
        for aluno in alunos:
            card = MDCard(
                orientation="vertical",
                padding=dp(16),
                size_hint=(1, None),
                height=dp(100),
                elevation=1,
                radius=[5],
                md_bg_color=(0.95, 0.95, 0.95, 1)
            )
            
            nome_label = MDLabel(
                text=aluno["nome_aluno"],
                theme_text_color="Primary",
                font_style="H6",
                size_hint_y=None,
                height=dp(30)
            )
            
            turma_label = MDLabel(
                text=f"Turma: {aluno['turma']}",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(20)
            )
            
            horarios_text = "Horários: "
            if aluno.get("manha_ida", False):
                horarios_text += "Ida Manhã, "
            if aluno.get("meiodia_ida", False):
                horarios_text += "Ida Meio-dia, "
            if aluno.get("meiodia_volta", False):
                horarios_text += "Volta Meio-dia, "
            if aluno.get("tarde_volta", False):
                horarios_text += "Volta 18:30, "
            
            horarios_text = horarios_text.rstrip(", ")
            
            horarios_label = MDLabel(
                text=horarios_text,
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(20)
            )
            
            card.add_widget(nome_label)
            card.add_widget(turma_label)
            card.add_widget(horarios_label)
            
            self.content_layout.add_widget(card)
    
    def carregar_dados(self):
        try:
            if os.path.exists(self.arquivo_dados):
                with open(self.arquivo_dados, 'r') as arquivo:
                    self.estudantes = json.load(arquivo)
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            self.estudantes = []
    
    def salvar_dados(self):
        try:
            with open(self.arquivo_dados, 'w') as arquivo:
                json.dump(self.estudantes, arquivo)
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")
    
    def salvar_contas(self):
        try:
            with open(self.arquivo_contas, 'w') as arquivo:
                json.dump(self.contas, arquivo)
        except Exception as e:
            print(f"Erro ao salvar contas: {e}")


if __name__ == "__main__":
    TransporteApp().run()
