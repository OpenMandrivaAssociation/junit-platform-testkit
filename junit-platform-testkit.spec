Name:		junit-platform-testkit
Version:	6.0.3
Release:	1
Summary:	JUnit Platform test kit
Group:		Development/Java
License:	EPL-2.0
URL:		https://junit.org/junit5/
# Same tag as junit6. Spock 2.4 calls EngineTestKit from this module.
# The other Platform jars stay in junit6. This module is compiled with
# javac. The Gradle tool is not invoked. module-info.java is not
# compiled; the jar uses Automatic-Module-Name, as the junit6 jars do.
Source0:	junit-framework-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	javapackages-filesystem
BuildRequires:	mvn(org.assertj:assertj-core)
BuildRequires:	mvn(org.opentest4j:opentest4j)
BuildRequires:	mvn(org.junit.platform:junit-platform-commons) = %{version}
BuildRequires:	mvn(org.junit.platform:junit-platform-engine) = %{version}
BuildRequires:	mvn(org.junit.platform:junit-platform-launcher) = %{version}
BuildRequires:	mvn(org.junit.jupiter:junit-jupiter-api) = %{version}
BuildRequires:	mvn(org.junit.jupiter:junit-jupiter-engine) = %{version}
BuildRequires:	mvn(org.apiguardian:apiguardian-api)
BuildRequires:	mvn(org.jspecify:jspecify)
BuildRequires:	mvn(net.bytebuddy:byte-buddy)

%description
org.junit.platform:junit-platform-testkit %{version}. EngineTestKit
discovers and executes one TestEngine and checks the recorded events.
The sources are compiled with javac at release 17.

%prep
%autosetup -n junit-framework-r%{version} -p1
find . -type f \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -print > binaries.list
find . -type d -name '*.jar' -print >> binaries.list
if [ -s binaries.list ]; then
	cat binaries.list
	exit 1
fi
find junit-platform-testkit/src/main/java -name '*.java' ! -name 'module-info.java' | sort > sources.list
test "$(wc -l < sources.list)" -eq 16
test -f junit-platform-testkit/src/main/java/module-info.java

%build
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
for jar in \
	assertj-core.jar \
	opentest4j/opentest4j.jar \
	junit-platform-commons-%{version}.jar \
	junit-platform-engine-%{version}.jar \
	junit-platform-launcher-%{version}.jar \
	apiguardian-api.jar \
	jspecify.jar \
	byte-buddy.jar
do
	test -s "%{_javadir}/$jar"
done
CP="%{_javadir}/assertj-core.jar:%{_javadir}/opentest4j/opentest4j.jar:%{_javadir}/junit-platform-commons-%{version}.jar:%{_javadir}/junit-platform-engine-%{version}.jar:%{_javadir}/junit-platform-launcher-%{version}.jar:%{_javadir}/apiguardian-api.jar:%{_javadir}/jspecify.jar"
mkdir -p classes
javac --release 17 -encoding UTF-8 -Xlint:-options,-removal -proc:none \
	-cp "$CP" -d classes @sources.list
test "$(find classes -name '*.class' | wc -l)" -eq 20
javap -v -classpath classes org.junit.platform.testkit.engine.EngineTestKit | grep -F -q 'major version: 61'
printf '%s\n' 'Manifest-Version: 1.0' 'Automatic-Module-Name: org.junit.platform.testkit' > manifest.mf
jar cfm junit-platform-testkit.jar manifest.mf -C classes .
jar i junit-platform-testkit.jar
jar tf junit-platform-testkit.jar | grep -F -qx 'org/junit/platform/testkit/engine/EngineTestKit.class'
desc=$(jar --describe-module --file junit-platform-testkit.jar)
printf '%s\n' "$desc" | grep -F -q 'org.junit.platform.testkit'
if printf '%s\n' "$desc" | grep -F -q 'Unable'; then
	printf '%s\n' "$desc"
	exit 1
fi

cat > junit-platform-testkit.pom << END
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.junit.platform</groupId>
  <artifactId>junit-platform-testkit</artifactId>
  <version>%{version}</version>
  <name>JUnit Platform Test Kit</name>
  <description>EngineTestKit for discovering and executing a TestEngine.</description>
  <url>https://junit.org/junit5/</url>
  <licenses>
    <license>
      <name>EPL-2.0</name>
      <url>https://www.eclipse.org/legal/epl-2.0/</url>
      <distribution>repo</distribution>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>org.assertj</groupId>
      <artifactId>assertj-core</artifactId>
      <version>3.27.7</version>
    </dependency>
    <dependency>
      <groupId>org.opentest4j</groupId>
      <artifactId>opentest4j</artifactId>
      <version>1.3.0</version>
    </dependency>
    <dependency>
      <groupId>org.junit.platform</groupId>
      <artifactId>junit-platform-commons</artifactId>
      <version>%{version}</version>
    </dependency>
    <dependency>
      <groupId>org.junit.platform</groupId>
      <artifactId>junit-platform-engine</artifactId>
      <version>%{version}</version>
    </dependency>
    <dependency>
      <groupId>org.junit.platform</groupId>
      <artifactId>junit-platform-launcher</artifactId>
      <version>%{version}</version>
    </dependency>
    <dependency>
      <groupId>org.apiguardian</groupId>
      <artifactId>apiguardian-api</artifactId>
      <version>1.1.2</version>
      <optional>true</optional>
    </dependency>
    <dependency>
      <groupId>org.jspecify</groupId>
      <artifactId>jspecify</artifactId>
      <version>1.0.0</version>
      <optional>true</optional>
    </dependency>
  </dependencies>
</project>
END

%install
set -eo pipefail
sysjar install --buildroot %{buildroot} \
	--artifact junit-platform-testkit.pom:junit-platform-testkit.jar \
	--file-name junit-platform-testkit-%{version} \
	--filelist .mfiles-mod
index="%{buildroot}/usr/share/sysjar/index/org.junit.platform/junit-platform-testkit.sysjar"
test -f "$index"
/bin/mv "$index" "%{buildroot}/usr/share/sysjar/index/org.junit.platform/junit-platform-testkit-%{version}.sysjar"
sed -i "s|/usr/share/sysjar/index/org.junit.platform/junit-platform-testkit\\.sysjar|/usr/share/sysjar/index/org.junit.platform/junit-platform-testkit-%{version}.sysjar|" .mfiles-mod
grep -F -q '"version": "%{version}"' "%{buildroot}/usr/share/sysjar/index/org.junit.platform/junit-platform-testkit-%{version}.sysjar"
/bin/cp -f .mfiles-mod .mfiles
test -s %{buildroot}%{_javadir}/junit-platform-testkit-%{version}.jar

%check
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
JAR=%{buildroot}%{_javadir}/junit-platform-testkit-%{version}.jar
test -s "$JAR"
mkdir -p check
cat > check/Smoke.java << 'END'
import static org.junit.platform.engine.discovery.DiscoverySelectors.selectClass;

import org.junit.jupiter.api.Test;
import org.junit.platform.testkit.engine.EngineTestKit;

public class Smoke {
    @Test
    void adds() {
        if (2 + 2 != 4) {
            throw new AssertionError("math");
        }
    }

    public static void main(String[] args) {
        EngineTestKit.engine("junit-jupiter")
            .selectors(selectClass(Smoke.class))
            .execute()
            .testEvents()
            .assertStatistics(stats -> stats.started(1).succeeded(1));
        System.out.println("testkit_ok 1");
    }
}
END
CP="$JAR:%{_javadir}/assertj-core.jar:%{_javadir}/opentest4j/opentest4j.jar:%{_javadir}/junit-platform-commons-%{version}.jar:%{_javadir}/junit-platform-engine-%{version}.jar:%{_javadir}/junit-platform-launcher-%{version}.jar:%{_javadir}/junit-jupiter-api-%{version}.jar:%{_javadir}/junit-jupiter-engine-%{version}.jar:%{_javadir}/byte-buddy.jar"
javac --release 17 -encoding UTF-8 -proc:none -cp "$CP" -d check check/Smoke.java
"$JAVA_HOME/bin/java" -cp "check:$CP" Smoke > check/out.txt
cat check/out.txt
grep -F -qx 'testkit_ok 1' check/out.txt

%files -f .mfiles
%doc README.md
%license LICENSE.md
