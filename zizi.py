import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.members = True  # Important pour on_member_join
intents.message_content = True  # Pour certaines commandes msg

bot = commands.Bot(command_prefix="/", intents=intents)

# -- CONSTANTES (à adapter) --
ROLE_AUTOROLE_ID = 1389381118532522125  # rôle auto join
CHANNEL_WELCOME_ID = 1389381125616435370  # channel bienvenue
ROLE_MUTE_ID = 1389381119505600654  # rôle mute

# -- EVENT --

@bot.event
async def on_member_join(member):
    try:
        role = member.guild.get_role(ROLE_AUTOROLE_ID)
        if role:
            await member.add_roles(role)
        channel = member.guild.get_channel(CHANNEL_WELCOME_ID)
        if channel:
            await channel.send(f"{member.mention} Bienvenue dans le serveur !")
    except Exception as e:
        print(f"Erreur on_member_join: {e}")

# -- COMMANDES SLASH --

@bot.tree.command(name="ban", description="Bannir un membre")
@app_commands.describe(member="Membre à bannir", reason="Raison du ban")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison donnée"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"{member} a été banni pour : {reason}")

@bot.tree.command(name="unban", description="Débannir un membre (par ID)")
@app_commands.describe(user_id="ID de l'utilisateur à débannir")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_id: str):
    banned_users = await interaction.guild.bans()
    user = None
    for ban_entry in banned_users:
        if str(ban_entry.user.id) == user_id:
            user = ban_entry.user
            break
    if user:
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"{user} a été débanni.")
    else:
        await interaction.response.send_message("Utilisateur non trouvé dans la liste des bannis.", ephemeral=True)

@bot.tree.command(name="kick", description="Expulser un membre")
@app_commands.describe(member="Membre à expulser", reason="Raison")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison donnée"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"{member} a été expulsé pour : {reason}")

@bot.tree.command(name="mute", description="Mettre un membre en muet (mute)")
@app_commands.describe(member="Membre à muter", reason="Raison")
@app_commands.checks.has_permissions(manage_roles=True)
async def mute(interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison donnée"):
    mute_role = interaction.guild.get_role(ROLE_MUTE_ID)
    if mute_role:
        await member.add_roles(mute_role, reason=reason)
        await interaction.response.send_message(f"{member} a été mute pour : {reason}")
    else:
        await interaction.response.send_message("Le rôle mute n'existe pas, contacte un admin.", ephemeral=True)

@bot.tree.command(name="unmute", description="Enlever le mute d'un membre")
@app_commands.describe(member="Membre à démute")
@app_commands.checks.has_permissions(manage_roles=True)
async def unmute(interaction: discord.Interaction, member: discord.Member):
    mute_role = interaction.guild.get_role(ROLE_MUTE_ID)
    if mute_role and mute_role in member.roles:
        await member.remove_roles(mute_role)
        await interaction.response.send_message(f"{member} a été unmute.")
    else:
        await interaction.response.send_message(f"{member} n'est pas mute.", ephemeral=True)

@bot.tree.command(name="msg", description="Envoyer un message via le bot dans un channel")
@app_commands.describe(channel="Salon", message="Message à envoyer")
@app_commands.checks.has_permissions(manage_messages=True)
async def msg(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
    await channel.send(message)
    await interaction.response.send_message(f"Message envoyé dans {channel.mention}")

# Commandes supplémentaires utiles

@bot.tree.command(name="avatarinfo", description="Afficher des infos détaillées sur l'avatar d'un membre")
@app_commands.describe(member="Membre à afficher")
async def avatarinfo(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    avatar = member.avatar
    embed = discord.Embed(title=f"Avatar de {member}", color=discord.Color.purple())
    embed.set_image(url=avatar.url)
    embed.add_field(name="URL", value=avatar.url, inline=False)
    embed.add_field(name="Taille (pixels)", value=f"{avatar.width}x{avatar.height}", inline=True)
    embed.add_field(name="Animation", value="Oui" if avatar.is_animated() else "Non", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="servericon", description="Afficher l'icône du serveur")
async def servericon(interaction: discord.Interaction):
    icon = interaction.guild.icon
    if icon:
        await interaction.response.send_message(icon.url)
    else:
        await interaction.response.send_message("Ce serveur n'a pas d'icône.", ephemeral=True)

@bot.tree.command(name="userinfo_full", description="Infos détaillées sur un membre")
@app_commands.describe(member="Membre à afficher")
async def userinfo_full(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"Infos détaillées de {member}", color=discord.Color.blue())
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="Nom complet", value=str(member), inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Créé le", value=member.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=True)
    embed.add_field(name="Rejoint le", value=member.joined_at.strftime("%d/%m/%Y %H:%M:%S"), inline=True)
    embed.add_field(name="Status", value=str(member.status).title(), inline=True)
    embed.add_field(name="Activité", value=str(member.activity) if member.activity else "Aucune", inline=True)
    roles = [r.mention for r in member.roles if r.name != "@everyone"]
    embed.add_field(name=f"Rôles ({len(roles)})", value=" ".join(roles) if roles else "Aucun", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="userinfo_joinage", description="Depuis combien de temps un membre est sur le serveur")
@app_commands.describe(member="Membre à afficher")
async def userinfo_joinage(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    delta = datetime.utcnow() - member.joined_at.replace(tzinfo=None)
    jours = delta.days
    heures = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    await interaction.response.send_message(
        f"{member} est sur le serveur depuis {jours} jours, {heures} heures et {minutes} minutes."
    )

@bot.tree.command(name="serverroles", description="Liste tous les rôles du serveur")
async def serverroles(interaction: discord.Interaction):
    roles = interaction.guild.roles
    roles = [r.mention for r in roles if r.name != "@everyone"]
    if not roles:
        await interaction.response.send_message("Aucun rôle sur ce serveur.")
    else:
        msg = ", ".join(roles)
        chunks = [msg[i : i + 2000] for i in range(0, len(msg), 2000)]
        for i, chunk in enumerate(chunks):
            if i == 0:
                await interaction.response.send_message(chunk)
            else:
                await interaction.channel.send(chunk)

@bot.tree.command(name="count", description="Compte les membres, bots, en ligne, etc.")
async def count(interaction: discord.Interaction):
    guild = interaction.guild
    total = guild.member_count
    bots = sum(1 for m in guild.members if m.bot)
    humans = total - bots
    online = sum(1 for m in guild.members if m.status != discord.Status.offline)
    await interaction.response.send_message(
        f"Total membres: {total}\nHumains: {humans}\nBots: {bots}\nEn ligne (hors offline): {online}"
    )

@bot.tree.command(name="invite", description="Créer une invitation temporaire")
@app_commands.describe(channel="Salon où créer l'invitation", max_uses="Nombre max d'utilisations", max_age="Durée en secondes")
async def invite(interaction: discord.Interaction, channel: discord.TextChannel = None, max_uses: int = 1, max_age: int = 3600):
    channel = channel or interaction.channel
    link = await channel.create_invite(max_uses=max_uses, max_age=max_age, unique=True)
    await interaction.response.send_message(f"Invitation créée : {link.url}")

@bot.tree.command(name="nick", description="Changer le pseudo d'un membre")
@app_commands.checks.has_permissions(manage_nicknames=True)
@app_commands.describe(member="Membre", nickname="Nouveau pseudo")
async def nick(interaction: discord.Interaction, member: discord.Member, nickname: str):
    await member.edit(nick=nickname)
    await interaction.response.send_message(f"Le pseudo de {member} a été changé en {nickname}.")

@bot.tree.command(name="slowmode", description="Activer ou désactiver le slowmode d'un salon")
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.describe(channel="Salon", seconds="Durée du slowmode (0 pour désactiver)")
async def slowmode(interaction: discord.Interaction, seconds: int, channel: discord.TextChannel = None):
    channel = channel or interaction.channel
    if seconds < 0 or seconds > 21600:
        await interaction.response.send_message("Le slowmode doit être entre 0 et 21600 secondes.", ephemeral=True)
        return
    await channel.edit(slowmode_delay=seconds)
    msg = "désactivé" if seconds == 0 else f"activé avec un délai de {seconds} secondes"
    await interaction.response.send_message(f"Slowmode {msg} dans {channel.mention}.")

@bot.tree.command(name="lock", description="Verrouiller un salon")
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.describe(channel="Salon à verrouiller")
async def lock(interaction: discord.Interaction, channel: discord.TextChannel = None):
    channel = channel or interaction.channel
    overwrite = channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = False
    await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message(f"{channel.mention} est maintenant verrouillé.")

@bot.tree.command(name="unlock", description="Déverrouiller un salon")
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.describe(channel="Salon à déverrouiller")
async def unlock(interaction: discord.Interaction, channel: discord.TextChannel = None):
    channel = channel or interaction.channel
    overwrite = channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = None
    await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message(f"{channel.mention} est maintenant déverrouillé.")

# -- Gestion erreurs des permissions --

@ban.error
@unban.error
@kick.error
@mute.error
@unmute.error
@msg.error
@nick.error
@slowmode.error
@lock.error
@unlock.error
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("Tu n'as pas les permissions nécessaires pour cette commande.", ephemeral=True)
    else:
        await interaction.response.send_message(f"Erreur : {error}", ephemeral=True)

# -- Sync slash commands au démarrage --

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Connecté en tant que {bot.user} (ID: {bot.user.id})")
    print("Slash commands synchronisées !")

# -- Lancement du bot --

if __name__ == "__main__":
    TOKEN = "MTM4OTM3OTY2NTk4MjEyODI4OA.GgxV4_.fCATRY_cObeL9BbMKqLa2oLAIbffYES09DdFqA"
    bot.run(TOKEN)
