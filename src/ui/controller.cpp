#include "controller.hpp"
#include <QDebug>

namespace haasp {
namespace ui {

Controller::Controller(QObject *parent)
    : QObject(parent), m_aiOracle(new AiOracle(this))
{
    connect(m_aiOracle, &AiOracle::codeGenerated, this, &Controller::onCodeGenerated);
    connect(m_aiOracle, &AiOracle::errorOccurred, this, &Controller::onAiError);
}

Controller::~Controller()
{
    delete m_aiOracle;
}

void Controller::onRepositoryOpened()
{
    emit uiStateChanged("repository_opened");
    qDebug() << "Repository opened - initializing AI context";
}

void Controller::onRepositoryClosed()
{
    emit uiStateChanged("repository_closed");
}

void Controller::navigateTo(const QString &target)
{
    emit navigationRequested(target);
}

void Controller::generateCode(const QString &prompt, const QString &language)
{
    qDebug() << "Generating code with prompt:" << prompt << "language:" << language;
    m_aiOracle->generateCode(prompt, language);
}

void Controller::analyzeCurrentCode()
{
    // This would be called with current code from QML
    m_aiOracle->analyzeCode("/* Current code context */");
}

void Controller::refactorSelectedCode(const QString &requirements)
{
    // This would be called with selected code from QML
    m_aiOracle->refactorCode("/* Selected code */", requirements);
}

void Controller::onCodeGenerated(const QString &code, const QString &language)
{
    qDebug() << "AI generated code in" << language;
    emit codeGenerated(code, language);
}

void Controller::onAiError(const QString &error)
{
    qDebug() << "AI Error:" << error;
    emit aiError(error);
}

} // namespace ui
} // namespace haasp
