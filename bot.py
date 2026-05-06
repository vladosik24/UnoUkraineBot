import logging
import os
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route
from telegram import Update, InlineQueryResultCachedSticker
from telegram.ext import Application, InlineQueryHandler, CommandHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Отримуємо токен з середовища (безпечніше)
BOT_TOKEN = os.environ.get("8420308119:AAHG9Vd3s4ycYcQvg_MxLtpWUEUWup2hA2M")
if not BOT_TOKEN:
    raise ValueError("Не задано BOT_TOKEN у змінних середовища!")

# Fly.io автоматично надасть ці змінні
APP_NAME = os.environ.get("FLY_APP_NAME", "uno-ukraine-bot")
PORT = int(os.environ.get("PORT", "8080"))
WEBHOOK_URL = f"https://{APP_NAME}.fly.dev/webhook"

# Твій повний словник стікерів (встав свій)
SK = {
    "r0":"CAACAgIAAxkBAAIElWn3hkAZVsKDy1IPAAEbDm70D7gyhAACuqcAAvccuEtr5aj0iEW_FzsE",
    "r1":"CAACAgIAAxkBAAIEl2n3hkMenmPbZwgeafxaFq-IPhbGAAKNmAACELa4S8TYC4lnM-ogOwQ",
    "r2":"CAACAgIAAxkBAAIEmWn3hkT-PVn91cu61Ve7O0KtJ0fOAALFqwACMp3BS9fHXDtvKjGpOwQ",
    "r3":"CAACAgIAAxkBAAIEm2n3hkYHFQrkwBXgY2A7Rg1mJR1kAAJclQACYo7BSwxYMOROZhtPOwQ",
    "r4":"CAACAgIAAxkBAAIEnWn3hkfWXVOcGkc4DkLGRnyZImgqAAKTnQACfPu4S-Dbgr6abbKyOwQ",
    "r5":"CAACAgIAAxkBAAIEn2n3hke_ZHsQwbtIaWCQMAgB40CAAAI-mgACEoS5S3EU6SFu7fx7OwQ",
    "r6":"CAACAgIAAxkBAAIEoWn3hkjJEZhDJJNERSfo06DEpFUAAzmWAAIZisFLCl-b96OGnmc7BA",
    "r7":"CAACAgIAAxkBAAIEo2n3hkqOqM3uO3vtYDuk6gqf9GfxAAKHpwACvVfBS41I10__YZatOwQ",
    "r8":"CAACAgIAAxkBAAIEpWn3hkoQnc5gkg4oumm5K4nk2sY_AAISoAACTIK4S5EI3WuT_V4MOwQ",
    "r9":"CAACAgIAAxkBAAIEp2n3hksn4JX6Jr7PY9O7f8NFvpYQAAJOpgACrte5Sy-bvsIPbpgaOwQ",
    "rd2":"CAACAgIAAxkBAAIEqWn3hk_TRStMJTd2v1hGCq4GEUe4AAJSpQACaha4S8RGTPt-66XeOwQ",
    "rr":"CAACAgIAAxkBAAIEq2n3hlSR4DcbZ_-Gt7tANkK2GAedAAJTnAAC_Na4SwekWbt3zde6OwQ",
    "rs":"CAACAgIAAxkBAAIErWn3hlVkh1YgGptWbq9s5JWgD-dfAAJXmwACH0S4S1sd_ijsA0-kOwQ",
    "y0":"CAACAgIAAxkBAAIE1Gn3h7EhRNhm9uYdvVEQCE8MqcXDAAInmAACJW3BS3TEy9oz2wSuOwQ",
    "y1":"CAACAgIAAxkBAAIE1Wn3h7FkRmnkckRnecDh2DeOcBsJAAKdpwACHbjAS_LNyXaN9TnzOwQ",
    "y2":"CAACAgIAAxkBAAIE1mn3h7GfE1JkJXQtVUQDfTyS7zH6AAJ9rgAC6zq5S2xoFem8KMw0OwQ",
    "y3":"CAACAgIAAxkBAAIE12n3h7FPdlZLzGpJoDA88xd--S75AALIpwACernBS-2dNXRerL_6OwQ",
    "y4":"CAACAgIAAxkBAAIE2Gn3h7EkClDmu0KPLhcXveR5VGizAAISoQACAq64SxlJHCBnMbRoOwQ",
    "y5":"CAACAgIAAxkBAAIE2Wn3h7EyheE1ivcqKoXnlhWcWU7VAAINxgACK1G5S3K_Dnw-HhzGOwQ",
    "y6":"CAACAgIAAxkBAAIE2mn3h7EocoTOilx5xv7NoRbeof0JAAL7oQACNtDAS34jc7WC-RXvOwQ",
    "y7":"CAACAgIAAxkBAAIE22n3h7HWWhmma_yNKSOhnbOtbv4BAAJqmQACG2_BS_BNLmv2WWJLOwQ",
    "y8":"CAACAgIAAxkBAAIE3Gn3h7HCC0AS8mEm3nHZpdVAWIPTAAJWsgAC-2nBS8hssf72QRCHOwQ",
    "y9":"CAACAgIAAxkBAAIE3Wn3h7Hod8i3UDiYRRI6n_FGoWPtAALFogACyoe4S6JlDmnIxMnhOwQ",
    "yd2":"CAACAgIAAxkBAAIE3mn3h7EvJ3HM7ad4t0XYYQj2GWk_AAI5oAACZz_BSxjjwToSIzfoOwQ",
    "yr":"CAACAgIAAxkBAAIE32n3h7H7lPUUUSQdv1H4D6LHJmrFAAIDngAClMLBSzmqRpwcFuXNOwQ",
    "ys":"CAACAgIAAxkBAAIE4Gn3h7H3k4kwl-fMNNQoyTFru4MNAALApwAC653BS3IH8FkQAYDwOwQ",
    "g0":"CAACAgIAAxkBAAIE-2n3iAwYbytYdXYg1silVeG2QlhfAAKklQACjdfBS-4utR0_5QuoOwQ",
    "g1":"CAACAgIAAxkBAAIE_Gn3iBLBIcJj2Fc9jfQxDGSWyc0NAAJQnQACkr3AS_V7FFBKGRhAOwQ",
    "g2":"CAACAgIAAxkBAAIE_Wn3iBLDzL6k5qqA0XsHR5csXvQ0AAI9owACPwW5S5Wm4yRlCU_BOwQ",
    "g3":"CAACAgIAAxkBAAIE_mn3iBN-Um-8XxrlhqLl9LaBRdabAAKrmwAC2Fa4S5bwcJ9_ozfeOwQ",
    "g4":"CAACAgIAAxkBAAIE_2n3iBRFPzq_RyX3nR-BPUK7bio6AAJ9owACgUy5Sym52DuXB4N4OwQ",
    "g5":"CAACAgIAAxkBAAIFAAFp94gVnC-DbVrI4JMMH8dFktwIywACa6EAAozZwEuVjZ6cwwEi1DsE",
    "g6":"CAACAgIAAxkBAAIFAWn3iBX1zlWMCyEBnGABthYytj35AAJslwACZ9S5S_U8CPHaZHiWOwQ",
    "g7":"CAACAgIAAxkBAAIFAmn3iBY6M9X8DXcrs7PaTiqZyLBUAAObAAIPrLlLObHthi9_d4Q7BA",
    "g8":"CAACAgIAAxkBAAIFA2n3iBaWbRS-QFrmNliSjBVGnvrAAALinQACSD65S-paL5WnlmSVOwQ",
    "g9":"CAACAgIAAxkBAAIFBGn3iBjvK2qNiyshVflH4S4hC2xkAALjnAACrei5S2vPD2JMcQbbOwQ",
    "gd2":"CAACAgIAAxkBAAIFBWn3iBgg1ZLgfjEBMvrDIH9Bd76kAAKxpgACOw7BS7s6FSfA8izYOwQ",
    "gr":"CAACAgIAAxkBAAIFBmn3iBk8AAGUQ2y4fAphu1zLrWdgEAACu6IAAuiVwUvrJtoPW9z5AzsE",
    "gs":"CAACAgIAAxkBAAIFB2n3iBm-B4O4zN7fmOrkRi8289keAALUoQACkOK4S-PTVKu9_o-cOwQ",
    "b0":"CAACAgIAAxkBAAIFImn3iHEQ1BSMyDydf_UNuFp2SZkVAAIvogACwTvAS_wWjL5dntjrOwQ",
    "b1":"CAACAgIAAxkBAAIFI2n3iHJwPs6aaBpW0ZnRzEMxE4-1AAKtngACb-DAS8fr__lRs3oNOwQ",
    "b2":"CAACAgIAAxkBAAIFJGn3iHKmWgl5oQds7C0SxoRNJDe0AAIUmgACaUa5S9Qv3H0S4RyDOwQ",
    "b3":"CAACAgIAAxkBAAIFJWn3iHM_dRq4fVOr5j8bn6OmygZRAAIumwACZXjASw8_-L7eeTZNOwQ",
    "b4":"CAACAgIAAxkBAAIFJmn3iHRmmWhnzciZGY0WF0JKE068AAJ8lQACCJLBSx-4oIR8J0bVOwQ",
    "b5":"CAACAgIAAxkBAAIFJ2n3iHQSj-bIskuv-hpoA8y36musAAI6pAACuRbBS0hiRwH0SektOwQ",
    "b6":"CAACAgIAAxkBAAIFKGn3iHXfw5HPJM9yDwJLZ9kceqREAAJwqwACabLAS8-vSIucsM3ZOwQ",
    "b7":"CAACAgIAAxkBAAIFR2n3iQKfN80EVUQQb7gDdxJ6zcUoAAIqngACsKW4S-pTMNxPY2QgOwQ",
    "b8":"CAACAgIAAxkBAAIFKmn3iHZ00weIAdJeW-tR1osPcbm_AAIGnwACIzO4S5jKyDivBonVOwQ",
    "b9":"CAACAgIAAxkBAAIFK2n3iHfdre5JDggqLhGON2HPAWk6AAI9ogACnqK5Sy65Wa2jWkYqOwQ",
    "bd2":"CAACAgIAAxkBAAIFLGn3iHfsF44hetZ0DDsgqM3lTu0zAAIBqQACeXC4S9Wvx-2Oh6-XOwQ",
    "br":"CAACAgIAAxkBAAIFLWn3iHg7Ao6U2vSut-nCsmVe5sJIAALapAACXPi4S8_16WdWbbTWOwQ",
    "bs":"CAACAgIAAxkBAAIFLmn3iHpIjloG82MBPb09jZFn3KHfAALwowACof_ASzJ4oFN3t8WUOwQ",
    "wild":"CAACAgIAAxkBAAIFWWn3iUsmpx9YqO0k95iUJpItOr60AAJ2mgACBN3BS89ZeVOSofTjOwQ",
    "wd4":"CAACAgIAAxkBAAIFWmn3iU1xzZuhAQhs12sHic1maq3vAAIxlwACiiPBS37YKZFL3f92OwQ",
}

async def start(update: Update, context):
    await update.message.reply_text("🃏 Привіт! Гра готова.")

async def inline_query(update: Update, context):
    hand = ["r0", "y5", "wild", "wd4", "b2"]  # тестова рука
    results = []
    for i, card_code in enumerate(hand):
        sticker_id = SK.get(card_code)
        if sticker_id:
            results.append(InlineQueryResultCachedSticker(id=str(i), sticker_file_id=sticker_id))
    await update.inline_query.answer(results, cache_time=0)

async def webhook(request: Request):
    application = request.app.state.application
    if request.method == "POST":
        try:
            data = await request.json()
            update = Update.de_json(data, application.bot)
            await application.process_update(update)
            return Response(status_code=200)
        except Exception as e:
            logger.error(f"Помилка: {e}")
            return Response(status_code=500)
    return PlainTextResponse("OK")

async def health(request: Request):
    return PlainTextResponse("OK")

async def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(InlineQueryHandler(inline_query))
    
    await application.bot.set_webhook(url=WEBHOOK_URL)
    logger.info(f"Вебхук встановлено: {WEBHOOK_URL}")
    
    app = Starlette(routes=[
        Route("/webhook", webhook, methods=["POST"]),
        Route("/health", health, methods=["GET"]),
        Route("/", health, methods=["GET"]),
    ])
    app.state.application = application
    
    config = uvicorn.Config(app, host="0.0.0.0", port=PORT)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
