#pragma once

#include <QObject>
#include "../nucleus/ai_oracle.hpp"

namespace haasp {
namespace ui {

class Controller : public QObject
{
    Q_OBJECT

public:
    explicit Controller(QObject *parent = nullptr);
    ~Controller();

    AiOracle* aiOracle() const { return m_aiOracle; }

signals:
    void uiStateChanged(const QString &state);
    void navigationRequested(const QString &target);
    void codeGenerated(const QString &code, const QString &language);
    void aiError(const QString &error);

public slots:
    void onRepositoryOpened();
    void onRepositoryClosed();
    void navigateTo(const QString &target);
    void generateCode(const QString &prompt, const QString &language = "cpp");
    void analyzeCurrentCode();
    void refactorSelectedCode(const QString &requirements);

private slots:
    void onCodeGenerated(const QString &code, const QString &language);
    void onAiError(const QString &error);

private:
    AiOracle *m_aiOracle;
};

} // namespace ui
} // namespace haasp
