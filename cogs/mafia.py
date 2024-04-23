import disnake
import asyncio
import random

from disnake.ext import commands


class StartGame(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        
    @commands.Cog.listener()  
    async def on_ready(self):
        print("Бот готовий до праці!")

    @commands.slash_command(name = 'start', description= 'Щоб почати гру, введи спочатку назву гри, а потім перелік гравців, яких ти запрошуєш')
    async def start(self, inter, name: str, player1: disnake.Member, player2: disnake.Member, player3: disnake.Member, player4: disnake.Member=None, player5: disnake.Member=None, player6: disnake.Member=None, player7: disnake.Member=None, player8: disnake.Member=None, player9: disnake.Member=None, player10: disnake.Member=None):
        #Визначаємо дані з команди: сервер та автора
        guild = inter.author.guild
        author = inter.author
        players_checker = [player1, player2, player3, player4, player5, player6, player7, player8, player9, player10]
        players = []
        self.members = []
        for i in players_checker:
            if i != None:
                players.append(i)
            
        #Додаємо в наш список усіх гравців
        for player in players:
            self.members.append(player)
        self.members.append(author)

        #Визначаємо їх як юзерів
        await asyncio.sleep(1)
        await inter.send(embed = disnake.Embed(title = "Запрошення гравцям відправлено!", description="Очікуйте на початок гри.", color = 0x000000))

        #Створюємо словник, завдяки якому будемо перевіряти чи прийняли запрошення гравці
        checker = {}

        #Buttons
        class Join(disnake.ui.View):
            def __init__ (self):
                super().__init__(timeout=20.0)
                self.result = False

            @disnake.ui.button(label="Приєднатися!", style=disnake.ButtonStyle.green)
            async def join(self, button:disnake.Button, interaction:disnake.Interaction):
                self.result = True
                await interaction.response.send_message("Вибір зроблено!")
                self.stop()

            @disnake.ui.button(label="Відмовитися!", style=disnake.ButtonStyle.red)
            async def dont_join(self, button:disnake.Button, interaction:disnake.Interaction):
                await interaction.response.send_message("Вибір зроблено!")
                self.stop()
        
        #Надсилаємо запрошення гравцям
        tasks = []
        for player in players:
            async def join(player):
                view = Join()
                await player.send(embed=disnake.Embed(title=f"Запрошення в гру \"{name}\" від {author}", description=f"Щоб увійти в гру \"{name}\" нажміть на кнопку \"Приєднатися!\"", color = 0xff0000), view=view)
                await view.wait()
                return view.result
            tasks.append(join(player))
            
        # Перевірка запрошень
        values = await asyncio.gather(*tasks)
        count = 0
        for player in range(len(self.members)-1):
            checker[player] = values[count]
            count+=1

        #перевірка запрошень
        didntJoinList = []
        for player in checker:
            if checker[player] == True:
                pass
            else:
                didntJoinList.append(player)

        #Надсилання результату та початок гри
        if len(didntJoinList) != 0:
            await inter.send(embed=disnake.Embed(title=f"Гру відмінено! Дехто не прийняв запрошення", color=0x000000))
        else:
            await inter.send(embed=disnake.Embed(title="Усі прийняли запрошення!", description="Очікуйте на початок гри", color=0xff0000))
            g = Game(self.bot, self.members, name, guild)
            await asyncio.sleep(2)
            await inter.send(embed=disnake.Embed(title="Гра починається.", description=f"Перейдіть в канал {name}", color=0x000000))
            await g.game_preparation()

    @commands.slash_command(name='help', description= 'Щоб почати гру, введи спочатку назву гри, а потім перелік гравців, яких ти запрошуєш')
    async def help(self, inter):
        author = inter.author
        embed = disnake.Embed(title=f"Привіт, {author}!", description="Це інформація про бота!", color = 0xffffff)
        embed.set_author(name="Mafia", icon_url="https://i.pinimg.com/564x/dc/a8/0b/dca80b34c94c2f25089b98e08503121a.jpg")
        embed.set_thumbnail(url="https://i.pinimg.com/564x/3a/0a/17/3a0a1753db493f176ec0b32b63302833.jpg")
        embed.set_footer(
        text="by sp1vak",
        icon_url="https://i.pinimg.com/564x/dc/a8/0b/dca80b34c94c2f25089b98e08503121a.jpg",
        )
        embed.set_image(url="https://i.pinimg.com/564x/ee/13/1f/ee131f1eb4316fdd9dc070addddda27b.jpg")
        embed.add_field(name="Команди", value="У цьому боті тіки одна команда окрім `/help` - `/start`. Приймає такі параметри: `назва гри`, `перший гравець`, `другий гравець`, `третій гравець.`...(максимальна кількість гравців - 10)", inline=False)
        embed.add_field(name="Початок гри", value="Після вводу команди гравцям приходе запрошення. Коли всі прийняли, починається гра.", inline=True)
        embed.add_field(name="Вибір жертви", value="Після початку гри, гравцям видаються ролі: два мирних, вбивця, доктор. Гра починається з вибору вбивці, кого вбити. Після його вибіру йде доктор.", inline=True)
        embed.add_field(name="Обговорення", value=" Якщо доктор вгадав кого вибрав вбивця, той залишається живий. Якщо ж не вгадує, то ви втрачаєте одного гравця. Після цього хвилина обговорення.")
        embed.add_field(name="Голосування", value="Коли ви все обговорили, вибираєте проти кого голосувати.")
        embed.add_field(name="Нехай щастить!", value="Надіюсь, тобі ця інформація допомогла. На все добре!")
        await inter.send(embed=embed, ephemeral=True)



class Game(commands.Cog):
    def __init__(self, bot, members, nameofgame, guild):
        self.members = members
        self.nameofgame = nameofgame
        self.guild = guild
        self.members_name_wtht_don = []
        self.bot = bot
        self.killed_list = []


    async def game_preparation(self):
        """підготовка до гри: створювання ролей, каналів, видача прав(фіміністкам не видаємо)"""
        #Створюємо роль гри та роль вбитої людини, яку будемо видавати тим, кого вбили або вибрали в голосуванні
        await self.guild.create_role(name = self.nameofgame)#створення ролі звичайних гравців
        await self.guild.create_role(name='Вмер')# створення ролі для вбитих

        self.rolegame = disnake.utils.get(self.guild.roles, name = self.nameofgame)# засовуємо роль гравця в змінну
        self.roledead = disnake.utils.get(self.guild.roles, name = 'Вмер')# role for dead -> self.roledead

        #Визначаємо, хто буде доном, доктором, мирними жителями
        random.shuffle(self.members)
        self.peaceful_list = []
        for member in self.members:
            await member.add_roles(self.rolegame)
        self.don = self.members[0]
        self.doctor = self.members[1]
        for member in self.members[2:]:
            self.peaceful_list.append(member)
        print('don: ', self.don)
        print('doctor: ', self.doctor)

        self.members_name_wtht_don.append(self.doctor)
        for member in self.peaceful_list:
            self.members_name_wtht_don.append(member)


        #Для голосування
        self.voting = {None: 0}
        for member in self.members:
            self.voting[member] = 0

        #Створювання текстового каналу, де буде проводитися гра та видання прав
        await self.guild.create_text_channel(self.nameofgame)
        self.channel = disnake.utils.get(self.guild.channels, name=self.nameofgame)
        await self.channel.set_permissions(self.guild.default_role, speak=False, send_messages = False, read_message_history=False, read_messages = False)
        await self.channel.set_permissions(self.rolegame, speak=True,send_messages=True,read_message_history=True,read_messages=True)
        await self.channel.set_permissions(self.roledead, speak=False, send_messages = False, read_message_history=True, read_messages = True)

        #Повідомлення гравців про їхню роль
        await asyncio.sleep(5)
        
        await self.channel.send(embed = disnake.Embed(title="Гра підібрала ваші ролі.", description="Перейдіть в приватні повідомлення з ботом", color = 0x000000))
        await asyncio.sleep(2)
        await self.don.send(embed = disnake.Embed(title = 'Ти вбивця', description='Убий всіх, поки не вбили тебе', color = 0xff0000))
        await self.doctor.send(embed = disnake.Embed(title= 'Ти доктор', description='Твоя ціль - лікувати людей та знаходити вбивцю', color = 0xffffff))
        for member in self.peaceful_list:
            await member.send(embed = disnake.Embed(title = 'Ти мирний', description='Знайди вбивцю та вижени його!', color = 0xffffff)) # - Розсилка ролей гравців

        #Повідомлення про початок гри
        await asyncio.sleep(5)
        await self.channel.send(embed = disnake.Embed(title = 'Гра почалась', color = 0x000000))# - Повідомлення про початок гри
        await asyncio.sleep(5)

        #Повідомлення про вечерю перед ніччю, та час для спілкування
        await self.channel.send(embed = disnake.Embed(title= 'Вечеря перед ніччю.', description='Намагайтеся виявити вбивцю!', color=0xff0000))
        await asyncio.sleep(60)# - Обговорення майбутньої ночі, гравці знайомляться один з одним.

        #початок гри.
        await self.game_2()


    async def game_2(self):
        """Вбивця та доктор виходять на нічну зміну."""
        await self.channel.set_permissions(self.rolegame, speak=False,send_messages=False,read_message_history=True,read_messages=True)

        await self.channel.send(embed=disnake.Embed(title="Настала ніч...", description="Намагайся вижити!", color = 0x000000))

        #Кнопки
        class ChooseDeath(disnake.ui.View):
            def __init__ (self, members_name_wtht_don):
                super().__init__(timeout=20.0)
                self.killed = None
                self.members_name_wtht_don = members_name_wtht_don

                for member in self.members_name_wtht_don:
                    if member != '---':
                        button = disnake.ui.Button(style=disnake.ButtonStyle.red, label=str(member))

                        async def button_callback(self, interaction: disnake.MessageInteraction, member=member):
                            self.killed = member
                            await interaction.response.send_message("Обрано!")#if it works, dont touch it
                            self.stop()

                        button.callback = button_callback.__get__(self)
                        self.add_item(button)

            @disnake.ui.button(label="Пропустити", style = disnake.ButtonStyle.blurple)
            async def skip(self, button:disnake.Button, inter:disnake.CommandInteraction):
                await inter.response.send_message("Вибір зроблено!")
                self.stop()

        view = ChooseDeath(self.members_name_wtht_don)
        await self.don.send(embed = disnake.Embed(title = 'Кого вб`ємо?',description="Обери, кого буде найвигідніше вбити!", color = 0xff0000), view=view)
        await view.wait()

        self.killed = view.killed

        await asyncio.sleep(2)

        class ChooseHeal(disnake.ui.View):
            def __init__ (self, members, killed):
                super().__init__(timeout=20.0)
                self.killed = None
                self.members = members

                for member in self.members:
                    if member != '---':
                        button = disnake.ui.Button(style=disnake.ButtonStyle.gray, label=str(member))

                        async def button_callback(self, interaction: disnake.MessageInteraction, member=member):
                            self.killed = member
                            await interaction.response.send_message("Обрано!")#if it works, dont touch it))
                            self.stop()

                        button.callback = button_callback.__get__(self)
                        self.add_item(button)

            @disnake.ui.button(label="Пропустити", style=disnake.ButtonStyle.blurple)
            async def skip(self, button:disnake.Button, inter:disnake.CommandInteraction):
                await inter.response.send_message("Вибір зроблено!")
                self.stop()

        if self.doctor not in self.killed_list:
            view = ChooseHeal(self.members, self.killed)
            await self.doctor.send(embed = disnake.Embed(title = 'До кого в дім зайдемо?', description="Обери, кого лікуватимеш цієї ночі.", color = 0xffffff), view=view)
            await view.wait()
            await asyncio.sleep(2)

        if self.killed in self.members:
            self.members[self.members.index(self.killed)] = '---'
            self.members_name_wtht_don[self.members_name_wtht_don.index(self.killed)] = '---'
        
        await asyncio.sleep(1)

        #Оголошення, кого вбили чи нікого
        if self.killed == None:
            await self.channel.send(embed=disnake.Embed(title='Ніч пройшла!', description='Цієї ночі нікого не вбили!', color = 0xffffff))
        else:
            await self.channel.send(embed=disnake.Embed(title="Ніч пройшла!", description=f'{self.killed} покидає нас...', color = 0xff0000))
            await self.killed.add_roles(self.roledead)
            await self.killed.remove_roles(self.rolegame)
            self.killed_list.append(self.killed)

        #Підрахунок вбитих
        count = 0
        for member in self.members:
            if member != '---':
                count +=1
        if count <= 2:
            await self.over_game()
            await self.channel.send(embed=disnake.Embed(title="Дон виграв"))
        elif count > 2:
            await self.voting_game()


    async def voting_game(self):
        """Голосування, хто вбивця"""
        #Обговорення
        await self.channel.set_permissions(self.rolegame, speak=True,send_messages=True,read_message_history=True,read_messages=True)
        await self.channel.send(embed = disnake.Embed(title = "Обговорення. У вас одна хвилина", description="Обговоріть вбивцю, та проголосуйте"))

        #Кнопки для голосування
        class Vote(disnake.ui.View):
            def __init__ (self, members):
                super().__init__(timeout=100.0)
                self.vote = None
                self.members = members

                for member in self.members:
                    if member != '---':
                        button = disnake.ui.Button(style=disnake.ButtonStyle.red, label=str(member))

                        async def button_callback(self, interaction: disnake.MessageInteraction, member=member):
                            self.vote = member
                            await interaction.response.send_message("Обрано!")#if it works, dont touch it))
                            self.stop()

                        button.callback = button_callback.__get__(self)
                        self.add_item(button)


            @disnake.ui.button(label="Пропустити", style=disnake.ButtonStyle.blurple)
            async def skip(self, button:disnake.Button, inter:disnake.CommandInteraction):
                await inter.response.send_message("Гравця було обрано!")
                self.stop()
                
        tasks = []
        for member in self.members:
            async def vote(member):
                if member != '---':
                    view = Vote(self.members)
                    await member.send(embed = disnake.Embed(title = "Голосування", description="Виберіть людину, що здається підозрілою", color = 0xffffff), view=view)
                    await view.wait()
                    return view.vote
                return 'kill'
            tasks.append(vote(member))

        values = await asyncio.gather(*tasks)

        for i in values:
            if i != 'kill':
                self.voting[i] += 1

        #Підрахунок та вибір гравця, якого кікаємо.
        voted = max(self.voting, key=self.voting.get)
        if voted != None:
            self.members[self.members.index(voted)] = '---'
            if voted in self.members_name_wtht_don:
                self.members_name_wtht_don[self.members_name_wtht_don.index(voted)] = '---'
            await voted.add_roles(self.roledead)
        self.killed_list.append(voted)

        #Підрахунок вбитих
        count = 0
        for member in self.members:
            if member != '---':
                count += 1
        await self.channel.send(embed = disnake.Embed(title="Підбито підсумки голосування", color=0xffffff))
        await asyncio.sleep(1)

        #Оголошення гравцям
        if voted == self.doctor:
            if count > 2:
                await self.channel.send(embed=disnake.Embed(title=f"Гравця {voted} викинуто", description="Він був доктором"))
                self.voting = {}
                for i in self.members:
                    if i != '---':
                        self.voting[i] = 0
                await self.game_2()
            elif count <= 2:
                await self.channel.send(embed=disnake.Embed(title=f"Дон виграв {self.don}", color=0xff0000))
                await self.over_game()
        elif voted == self.don:
            await self.channel.send(embed=disnake.Embed(title=f"Гравця {voted} викинуто", description="Він був доном", color=0x000000))
            await self.channel.send(embed=disnake.Embed(title="Дон програв!"))
            await self.over_game()
        elif voted in self.peaceful_list:
            if count > 2:
                await self.channel.send(embed=disnake.Embed(title=f"Гравця {voted} викинуто", description="Він був мирним жителем", color = 0x000000))
                self.peaceful_list.remove(voted)
                self.voting = {}
                for i in self.members:
                    if i !=  '---':
                       self.voting[i] = 0
                await self.game_2()
            elif count <= 2:
                await self.channel.send(embed=disnake.Embed(title="Дон виграв!"))
                await self.over_game()
        elif voted == None:
            await self.channel.send(embed=disnake.Embed(title="Більшість вирішила не голосувати!", description="На один шанс більше для вбивці?", color = 0x000000))
            await self.game_2()
    

    async def over_game(self):
        await self.channel.send(embed = disnake.Embed(title = f'Вбивцею був {self.don}'))
        await self.channel.send(embed = disnake.Embed(title='Гру видалено', description='Щоб створити нову, введіть команду /start назва гри', color = 0x000000))
        await asyncio.sleep(5)
        await self.channel.delete()
        await self.roledead.delete()
        await self.rolegame.delete()

def setup(bot):
    bot.add_cog(StartGame(bot))
